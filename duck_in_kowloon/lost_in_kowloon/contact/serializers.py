from rest_framework import serializers

from index.forms import phone_validator


class ContactSubmissionSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=3, max_length=100)
    phone = serializers.CharField(max_length=30, validators=[phone_validator])
    email = serializers.EmailField()
    message = serializers.CharField(max_length=500)
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)
    recaptchaToken = serializers.CharField(write_only=True)

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError("Invalid submission.")
        return value