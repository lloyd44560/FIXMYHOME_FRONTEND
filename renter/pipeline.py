from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from renter.models import User  # Adjust to your User model path

def verify_email(strategy, details, backend, user=None, *args, **kwargs):
    email = details.get('email')

    # Check if email exists in your User table
    if not User.objects.filter(email=email).exists():
        # Block the login
        messages.error(strategy.request, 'Google account is not registered. Please register first.')
        return redirect(reverse('login_renter'))  # Make sure 'login_renter' is the correct name in your urls.py
    else:
        print("Successffully logged in using GMAIL")
    # Otherwise, continue login
    return
