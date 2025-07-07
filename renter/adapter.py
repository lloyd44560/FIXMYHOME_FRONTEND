from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

from renter.models import Renter  # adjust if path differs
from django.contrib.auth.models import User


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Get email from social account's extra data
        email = sociallogin.account.extra_data.get('email')

        # If no matching user exists in Django's User model, redirect
        if email and not User.objects.filter(email=email).exists():
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse('no_account')))
