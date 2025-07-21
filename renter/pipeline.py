from social_core.exceptions import AuthForbidden
from django.contrib.auth.models import User
from django.contrib import messages
from renter.models import Renter  # Clean import thanks to __init__.py
from django.core.exceptions import PermissionDenied

def verify_email(strategy, details, backend, user=None, *args, **kwargs):
    email = details.get('email')

    if not User.objects.filter(email=email).exists():
        messages.error(strategy.request, 'Google account is not registered. Please register first.')
        raise AuthForbidden(backend)

    if not Renter.objects.filter(email=email).exists():
        messages.error(strategy.request, 'This Google account is not linked to a renter profile.')
        raise AuthForbidden(backend)

    return
