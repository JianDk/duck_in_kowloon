from smtplib import SMTPException
from types import SimpleNamespace
from unittest.mock import patch

from django.core import mail
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import DeadlineExceeded, PermissionDenied, ServiceUnavailable
from google.auth.exceptions import GoogleAuthError
from google.cloud import recaptchaenterprise_v1
from google.cloud.recaptchaenterprise_v1 import (
	RecaptchaEnterpriseServiceClient,
)
from rest_framework.test import APIClient

from utils.email.email.email import sendEmail
from utils.recaptcha.recaptcha_validation import validate_recaptcha

from .recaptcha import RecaptchaUnavailableError, verify_contact_token


@override_settings(
	RECAPTCHA_PROJECT_ID="test-project",
	RECAPTCHA_API_KEY="test-api-key",
	RECAPTCHA_SITE_KEY="test-site-key",
	RECAPTCHA_MIN_SCORE=0.5,
	RECAPTCHA_ALLOWED_HOSTNAMES=["localhost", "example.com"],
)
class RecaptchaVerificationTests(SimpleTestCase):
	def setUp(self):
		client_patch = patch("contact.recaptcha.recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient")
		self.client_class = client_patch.start()
		self.addCleanup(client_patch.stop)
		self.client = self.client_class.return_value.__enter__.return_value
		self.assessment = recaptchaenterprise_v1.Assessment(
			token_properties={
				"valid": True,
				"action": "contact_submit",
				"hostname": "localhost",
			},
			risk_analysis={"score": 0.9},
		)
		self.client.create_assessment.return_value = self.assessment

	def set_response(self, assessment):
		self.client.create_assessment.return_value = assessment

	def test_accepts_valid_token_and_sends_enterprise_assessment(self):
		self.set_response(self.assessment)
		self.assertTrue(verify_contact_token("test-token"))

		self.client_class.assert_called_once()
		self.assertEqual(
			set(self.client_class.call_args.kwargs), {"client_options"},
		)
		options = self.client_class.call_args.kwargs["client_options"]
		self.assertIsInstance(options, ClientOptions)
		self.assertEqual(options.api_key, "test-api-key")
		request = self.client.create_assessment.call_args.kwargs["request"]
		self.assertIsInstance(request, recaptchaenterprise_v1.CreateAssessmentRequest)
		self.assertEqual(request.parent, "projects/test-project")
		self.assertEqual(request.assessment.event.token, "test-token")
		self.assertEqual(request.assessment.event.site_key, "test-site-key")
		self.assertEqual(request.assessment.event.expected_action, "contact_submit")
		self.assertEqual(set(self.client.create_assessment.call_args.kwargs), {"request", "retry", "timeout"})
		self.assertIsNone(self.client.create_assessment.call_args.kwargs["retry"])
		self.assertEqual(self.client.create_assessment.call_args.kwargs["timeout"], 5)

	def test_rejects_missing_or_non_string_tokens_without_google_request(self):
		for token in (None, "", "   ", 123, {}, []):
			with self.subTest(token=token):
				self.assertFalse(verify_contact_token(token))
		self.client_class.assert_not_called()

	def test_rejects_invalid_action_hostname_or_token(self):
		for field, value in (
			("valid", False), ("action", "login"), ("action", ""),
			("hostname", "attacker.example"), ("hostname", ""),
			("hostname", "localhost.attacker.example"),
			("hostname", "example.com.attacker.example"),
			("hostname", "www.example.com"),
		):
			with self.subTest(field=field, value=value):
				assessment = recaptchaenterprise_v1.Assessment(self.assessment)
				setattr(assessment.token_properties, field, value)
				self.set_response(assessment)
				self.assertFalse(verify_contact_token("test-token"))

	def test_score_threshold_boundary(self):
		for score, accepted in ((0.0, False), (0.49, False), (0.5, True), (1.0, True)):
			with self.subTest(score=score):
				assessment = recaptchaenterprise_v1.Assessment(self.assessment)
				assessment.risk_analysis.score = score
				self.set_response(assessment)
				self.assertEqual(verify_contact_token("test-token"), accepted)

	def test_rejects_malformed_assessments(self):
		responses = [None, [], {}]
		for score in (-0.1, 1.1, float("nan"), float("inf")):
			assessment = recaptchaenterprise_v1.Assessment(self.assessment)
			assessment.risk_analysis.score = score
			responses.append(assessment)
		for assessment in responses:
			with self.subTest(assessment=assessment):
				self.set_response(assessment)
				with self.assertRaises(RecaptchaUnavailableError):
					verify_contact_token("test-token")

	def test_handles_google_transport_failures(self):
		for error in (
			DeadlineExceeded("Timed out"),
			ServiceUnavailable("Unavailable"),
			PermissionDenied("Forbidden"),
			GoogleAuthError("Authentication failed"),
			OSError("Connection failed"),
			ValueError("Invalid response"),
		):
			with self.subTest(error=type(error).__name__):
				self.client.create_assessment.side_effect = error
				with self.assertRaises(RecaptchaUnavailableError):
					verify_contact_token("test-token")

	def test_api_key_client_does_not_discover_default_credentials(self):
		with patch(
			"google.auth.default",
			side_effect=AssertionError("ADC must not be used"),
		) as discover:
			with RecaptchaEnterpriseServiceClient(
				client_options=ClientOptions(api_key="test-api-key"),
			):
				pass
		discover.assert_not_called()

	def test_client_authentication_failure_does_not_create_assessment(self):
		self.client_class.side_effect = GoogleAuthError("Credentials unavailable")
		with self.assertRaises(RecaptchaUnavailableError):
			verify_contact_token("test-token")
		self.client.create_assessment.assert_not_called()

	def test_rejects_missing_risk_analysis(self):
		self.set_response(recaptchaenterprise_v1.Assessment(
			token_properties=self.assessment.token_properties,
		))
		with self.assertRaises(RecaptchaUnavailableError):
			verify_contact_token("test-token")

	def test_rejects_missing_token_properties(self):
		self.set_response(recaptchaenterprise_v1.Assessment())
		self.assertFalse(verify_contact_token("test-token"))

	def test_missing_configuration_does_not_call_google(self):
		for setting, value in (
			("RECAPTCHA_PROJECT_ID", ""),
			("RECAPTCHA_API_KEY", ""),
			("RECAPTCHA_SITE_KEY", ""), ("RECAPTCHA_ALLOWED_HOSTNAMES", []),
		):
			with self.subTest(setting=setting), override_settings(**{setting: value}):
				with self.assertRaises(RecaptchaUnavailableError):
					verify_contact_token("test-token")
		self.client_class.assert_not_called()

	def test_invalid_threshold_does_not_call_google(self):
		for score in (-0.1, 1.1, float("nan"), float("inf"), None, "0.5", True):
			with self.subTest(score=score), override_settings(RECAPTCHA_MIN_SCORE=score):
				with self.assertRaises(RecaptchaUnavailableError):
					verify_contact_token("test-token")
		self.client_class.assert_not_called()

	@override_settings(
		EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
		EMAIL_ALIAS="contact@example.com",
		ALLOWED_HOSTS=["testserver"],
	)
	def test_api_uses_google_score_not_browser_score_before_sending(self):
		client = APIClient()
		payload = {
			"name": "Alex Visitor",
			"phone": "+45 12 34 56 78",
			"email": "alex@example.com",
			"message": "I would like to ask about your menu.",
			"recaptchaToken": "test-token",
			"score": 1.0,
		}
		self.assessment.risk_analysis.score = 0.1
		response = client.post(reverse("contact-submit"), payload, format="json")
		self.assertEqual(response.status_code, 403)
		self.assertEqual(len(mail.outbox), 0)

		self.assessment.risk_analysis.score = 0.9
		payload["score"] = 0.0
		response = client.post(reverse("contact-submit"), payload, format="json")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(mail.outbox), 1)
		self.assertNotIn("score", response.json())
		self.assertEqual(self.client.create_assessment.call_count, 2)


class RecaptchaValidationTests(SimpleTestCase):
	def setUp(self):
		self.request = SimpleNamespace(data={"recaptchaToken": "test-token"})
		verify_patch = patch(
			"utils.recaptcha.recaptcha_validation.verify_contact_token",
			return_value=True,
		)
		self.verify = verify_patch.start()
		self.addCleanup(verify_patch.stop)

	def test_valid_token_returns_success(self):
		result, status_code = validate_recaptcha(self.request)
		self.assertIs(result["success"], True)
		self.assertEqual(status_code, 200)
		self.verify.assert_called_once_with("test-token")

	def test_missing_or_invalid_token_never_calls_google(self):
		for token in (None, "", "   ", 123, {}, []):
			with self.subTest(token=token):
				self.request.data = {"recaptchaToken": token}
				result, status_code = validate_recaptcha(self.request)
				self.assertIs(result["success"], False)
				self.assertEqual(status_code, 400)
		self.request.data = {}
		self.assertEqual(validate_recaptcha(self.request)[1], 400)
		self.verify.assert_not_called()

	@override_settings(
		DEBUG=True,
		GOOGLE_RECAPTCHA_SITE_KEY="dev-recaptcha",
		GOOGLE_RECAPTCHA_SECRET_KEY="dev-recaptcha",
	)
	def test_debug_placeholders_do_not_bypass_verification(self):
		self.verify.return_value = False
		result, status_code = validate_recaptcha(self.request)
		self.assertIs(result["success"], False)
		self.assertEqual(status_code, 403)
		self.verify.assert_called_once_with("test-token")

	def test_unavailable_verification_returns_failure(self):
		self.verify.side_effect = RecaptchaUnavailableError("Unavailable")
		result, status_code = validate_recaptcha(self.request)
		self.assertIs(result["success"], False)
		self.assertEqual(status_code, 503)
		self.assertEqual(
			result["message"], "Security verification is unavailable.",
		)


@override_settings(
	EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
	EMAIL_ALIAS="contact@example.com",
	DEFAULT_FROM_EMAIL="contact@example.com",
	CONTACT_RECIPIENT_EMAIL="restaurant@example.com",
	ALLOWED_HOSTS=["testserver"],
)
class ContactSubmissionTests(SimpleTestCase):
	def setUp(self):
		self.client = APIClient()
		self.url = reverse("contact-submit")
		self.payload = {
			"name": "Alex Visitor",
			"phone": "+45 12 34 56 78",
			"email": "alex@example.com",
			"message": "I would like to ask about your menu.",
			"recaptchaToken": "test-token",
		}
		verify_patch = patch(
			"contact.rest_api.validate_recaptcha",
			return_value=({"success": True}, 200),
		)
		self.verify = verify_patch.start()
		self.addCleanup(verify_patch.stop)
		email_patch = patch("contact.rest_api.sendEmail", wraps=sendEmail)
		self.email_factory = email_patch.start()
		self.addCleanup(email_patch.stop)

	def submit(self, payload=None):
		return self.client.post(
			self.url, self.payload if payload is None else payload, format="json",
		)

	def test_verified_submission_uses_helper_and_sends_email(self):
		self.payload["message"] = "a" * 500
		response = self.submit()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), {"success": True})
		self.verify.assert_called_once()
		self.assertEqual(self.verify.call_args.args[0].data, self.payload)
		self.email_factory.assert_called_once()
		self.assertEqual(len(mail.outbox), 1)
		email = mail.outbox[0]
		self.assertEqual(email.from_email, "contact@example.com")
		self.assertEqual(email.to, ["contact@example.com"])
		self.assertEqual(email.reply_to, ["alex@example.com"])
		self.assertIn("Alex Visitor", email.body)
		self.assertIn(self.payload["message"], email.body)
		self.assertNotIn("test-token", email.body)

	def test_invalid_fields_do_not_verify_or_send_email(self):
		for field, value in (
			("name", "Al"), ("name", "   "), ("email", "invalid"),
			("phone", "abc"), ("message", ""), ("message", "a" * 501),
			("website", "https://spam.example"), ("message", ["unexpected"]),
		):
			with self.subTest(field=field, value=value):
				response = self.submit({**self.payload, field: value})
				self.assertEqual(response.status_code, 400)
				self.assertIn(field, response.json()["fieldErrors"])
		self.verify.assert_not_called()
		self.email_factory.assert_not_called()

	def test_missing_fields_do_not_verify_or_send_email(self):
		response = self.submit({})
		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			set(response.json()["fieldErrors"]),
			{"name", "phone", "email", "message", "recaptchaToken"},
		)
		self.verify.assert_not_called()
		self.email_factory.assert_not_called()

	def test_missing_or_invalid_token_does_not_send_email(self):
		for token in (None, "", " ", {}):
			with self.subTest(token=token):
				response = self.submit({**self.payload, "recaptchaToken": token})
				self.assertEqual(response.status_code, 400)
		self.verify.assert_not_called()
		self.email_factory.assert_not_called()

	def test_rejected_token_does_not_send_email(self):
		self.verify.return_value = (
			{"success": False, "message": "Security verification failed."}, 403,
		)
		self.assertEqual(self.submit().status_code, 403)
		self.email_factory.assert_not_called()

	def test_unavailable_verification_does_not_send_email(self):
		self.verify.return_value = (
			{"success": False, "message": "Security verification is unavailable."},
			503,
		)
		self.assertEqual(self.submit().status_code, 503)
		self.email_factory.assert_not_called()

	def test_invalid_json_does_not_verify_or_send_email(self):
		for body in ("{", "[]", "null", '"text"', b"\xff"):
			with self.subTest(body=body):
				response = self.client.post(self.url, data=body, content_type="application/json")
				self.assertEqual(response.status_code, 400)
		self.verify.assert_not_called()
		self.email_factory.assert_not_called()

	def test_non_json_request_does_not_verify_or_send_email(self):
		response = self.client.post(self.url, data={"name": "Alex"}, format="multipart")
		self.assertEqual(response.status_code, 415)
		self.verify.assert_not_called()
		self.email_factory.assert_not_called()

	def test_email_failure_does_not_report_success(self):
		for error in (SMTPException("SMTP unavailable"), OSError("Connection failed")):
			with self.subTest(error=type(error).__name__), patch(
				"django.core.mail.EmailMultiAlternatives.send", side_effect=error,
			):
				response = self.submit()
				self.assertEqual(response.status_code, 503)
				self.assertNotIn("success", response.json())

	def test_zero_emails_sent_does_not_report_success(self):
		with patch("django.core.mail.EmailMultiAlternatives.send", return_value=0):
			self.assertEqual(self.submit().status_code, 503)

	def test_csrf_is_required_before_verification_or_email(self):
		client = APIClient(enforce_csrf_checks=True)
		response = client.post(self.url, self.payload, format="json")
		self.assertEqual(response.status_code, 403)
		self.verify.assert_not_called()
		self.email_factory.assert_not_called()

	def test_valid_csrf_token_allows_verified_submission(self):
		client = APIClient(enforce_csrf_checks=True)
		self.assertEqual(client.get(reverse("contact")).status_code, 200)
		response = client.post(
			self.url, self.payload, format="json",
			HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(mail.outbox), 1)
