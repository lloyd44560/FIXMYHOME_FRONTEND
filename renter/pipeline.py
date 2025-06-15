from social_core.exceptions import AuthForbidden
from renter.models import User  # Replace with your actual User model

def verify_email(strategy, details, backend, user=None, *args, **kwargs):
    email = details.get('email')

    if not User.objects.filter(email=email).exists():
        # Block login if email not found in your system
        from django.contrib import messages
        messages.error(strategy.request, 'Google account is not registered. Please register first.')
        raise AuthForbidden(backend)  #  This will trigger the redirection to SOCIAL_AUTH_LOGIN_ERROR_URL

    return
