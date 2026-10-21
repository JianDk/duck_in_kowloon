from smtplib import SMTPException

from django.conf import settings
from django.core.mail import BadHeaderError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.email.email.email import sendEmail
from utils.recaptcha.recaptcha_validation import validate_recaptcha

from .serializers import ContactSubmissionSerializer


@method_decorator(csrf_protect, name='dispatch')
class ContactSubmissionView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        serializer = ContactSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'fieldErrors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        values = serializer.validated_data
        verification, verification_status = validate_recaptcha(request)
        if verification.get('success') is not True:
            return Response(
                {'error': verification['message']},
                status=verification_status,
            )

        body = (
            f"Name: {values['name']}\n"
            f"Email: {values['email']}\n"
            f"Phone: {values['phone']}\n\n"
            f"{values['message']}"
        )
        try:
            email = sendEmail(
                subject='Contact enquiry | Duck In Kowloon',
                textContent=body,
                htmlContent=None,
                fromEmail=settings.EMAIL_ALIAS,
                toEmail=[settings.EMAIL_ALIAS],
            )
            email.reply_to = [values['email']]
            sent = email.send(fail_silently=False)
        except (SMTPException, OSError, BadHeaderError):
            return Response(
                {'error': 'Your message could not be sent.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if sent != 1:
            return Response(
                {'error': 'Your message could not be sent.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({'success': True})