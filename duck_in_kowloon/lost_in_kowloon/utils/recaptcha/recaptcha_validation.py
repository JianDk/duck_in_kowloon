from contact.recaptcha import RecaptchaUnavailableError, verify_contact_token


def validate_recaptcha(request):
    token = request.data.get("recaptchaToken")
    if not isinstance(token, str) or not token.strip():
        return {
            "success": False,
            "message": "A security verification token is required.",
        }, 400

    try:
        verified = verify_contact_token(token)
    except RecaptchaUnavailableError:
        return {
            "success": False,
            "message": "Security verification is unavailable.",
        }, 503

    if not verified:
        return {
            "success": False,
            "message": "Security verification failed.",
        }, 403

    return {
        "success": True,
        "message": "Recaptcha validation passed.",
    }, 200
