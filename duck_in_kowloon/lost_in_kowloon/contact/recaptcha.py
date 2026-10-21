import math

from django.conf import settings
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import GoogleAPICallError
from google.auth.exceptions import GoogleAuthError
from google.cloud import recaptchaenterprise_v1


class RecaptchaUnavailableError(Exception):
    pass


def verify_contact_token(token):
    if not isinstance(token, str) or not token.strip():
        return False

    if not all((
        settings.RECAPTCHA_PROJECT_ID,
        settings.RECAPTCHA_API_KEY,
        settings.RECAPTCHA_SITE_KEY,
        settings.RECAPTCHA_ALLOWED_HOSTNAMES,
    )):
        raise RecaptchaUnavailableError("reCAPTCHA configuration is incomplete.")

    minimum_score = settings.RECAPTCHA_MIN_SCORE
    if (
        type(minimum_score) not in (int, float)
        or not 0 <= minimum_score <= 1
        or not math.isfinite(minimum_score)
    ):
        raise RecaptchaUnavailableError("reCAPTCHA score threshold must be between 0 and 1.")

    event = recaptchaenterprise_v1.Event()
    event.site_key = settings.RECAPTCHA_SITE_KEY
    event.token = token
    event.expected_action = "contact_submit"

    assessment = recaptchaenterprise_v1.Assessment()
    assessment.event = event

    project_name = f"projects/{settings.RECAPTCHA_PROJECT_ID}"

    request = recaptchaenterprise_v1.CreateAssessmentRequest()
    request.assessment = assessment
    request.parent = project_name

    try:
        with recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient(
            client_options=ClientOptions(api_key=settings.RECAPTCHA_API_KEY),
        ) as client:
            assessment = client.create_assessment(request=request, retry=None, timeout=5)
    except (GoogleAPICallError, GoogleAuthError, OSError, ValueError):
        raise RecaptchaUnavailableError("reCAPTCHA assessment could not be completed.") from None

    if not isinstance(assessment, recaptchaenterprise_v1.Assessment):
        raise RecaptchaUnavailableError("Invalid reCAPTCHA assessment response.")

    properties = assessment.token_properties
    if (
        not properties.valid
        or properties.action != "contact_submit"
        or properties.hostname not in settings.RECAPTCHA_ALLOWED_HOSTNAMES
    ):
        return False

    if not recaptchaenterprise_v1.Assessment.pb(assessment).HasField("risk_analysis"):
        raise RecaptchaUnavailableError("Missing reCAPTCHA risk analysis.")

    score = assessment.risk_analysis.score
    if not math.isfinite(score) or not 0 <= score <= 1:
        raise RecaptchaUnavailableError("Invalid reCAPTCHA risk score.")

    return score >= minimum_score