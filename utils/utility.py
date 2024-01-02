from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime, timedelta
import jwt


def send_html_email(to="", subject="", template="", context=None):
    if context is None:
        context = {}
    html_message = render_to_string(template_name=template, context=context)
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[to],
        # bcc=[settings.BCC_EMAIL],
    )
    email.content_subtype = "html"
    email.send()
    return True


# encode/encrypt token
def encode_token(email, minute=0):
    expiration = datetime.now() + timedelta(minutes=minute)
    payload = {'email': email, 'exp': expiration}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


# decode/decrypt token
def decode_token(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
