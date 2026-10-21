from django.core.mail import EmailMultiAlternatives

def sendEmail(
    subject : str,
    textContent : str,
    htmlContent : str,
    fromEmail : str,
    toEmail : list,
):
    """
        Creating the email instance. It does not send the email, but
        returns the email instance so that an attachment can be added and email sent
    """
    
    email = EmailMultiAlternatives(
        subject, 
        textContent, 
        fromEmail,
        toEmail
    )
    if htmlContent is not None:
        email.attach_alternative(htmlContent, "text/html")
    return email
            
        