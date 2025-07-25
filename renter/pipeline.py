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



def link_renter_to_user(strategy, details, user=None, *args, **kwargs):
    """
    After Google login, if there's a Renter with the same email, link it to the user.
    """
    if user and details.get('email'):
        email = details['email']
        try:
            renter = Renter.objects.filter(email=email).first()
            if renter and renter.user_id != user.id:
                renter.user = user
                renter.save()
        except Renter.DoesNotExist:
            pass
