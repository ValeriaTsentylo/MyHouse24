import secrets
import string

import requests
from allauth.account.models import EmailAddress
from django.conf import settings


def verify_recaptcha(recaptcha_response):
    data = {"secret": settings.RECAPTCHA_PRIVATE_KEY, "response": recaptcha_response}
    try:
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
        result = r.json()

        return result.get("success", False)

    except requests.exceptions.RequestException:
        return False


def is_email_verified(user):
    return EmailAddress.objects.filter(user=user, verified=True).exists()


def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(alphabet) for i in range(length))
    return password
