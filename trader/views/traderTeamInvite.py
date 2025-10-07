from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings

from trader.models import TraderRegistration
from trader.models import TeamMember
from django.contrib.auth.models import User

import json
import string
import random

@csrf_exempt
def invite_team_member(request, member_id):
    if request.method == 'POST':
        try:
            getTrader = TraderRegistration.objects.filter(user=request.user, isDirector=True).first()
            member = TeamMember.objects.get(pk=member_id)
            email = member.email

            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "User with this email already exists."}, status=400)

            # Generate random password
            generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Create Django User
            user = User.objects.create_user(
                username=email,
                email=email,
                password=generated_password,
                first_name=member.teamName,
                is_staff=True
            )

            # Create TraderRegistration for Team Member
            traderMember = TraderRegistration.objects.create(
                # Login Information
                user=user,
                name=member.teamName,
                email=email,
                # Company Details
                company_name=getTrader.company_name,
                company_address=getTrader.company_address,
                company_email=getTrader.company_email,
                company_landline=getTrader.company_landline,
                gst_registered=getTrader.gst_registered,
                abn=getTrader.abn,
                industry=getTrader.industry,
                # Set as Member
                isTeamMember=True,
                isDirector=False
            )

            member.user = user
            member.trader = traderMember
            member.save()

            # Send invite email
            from django.core.mail import send_mail
            send_mail(
                subject="Welcome to the Team!",
                message=(
                    f"Hi {member.teamName},\n\n"
                    f"You’ve been invited to join our team on FixMyHouse.\n\n"
                    f"Here are your login details:\n"
                    f"Email: {email}\n"
                    f"Temporary Password: {generated_password}\n\n"
                    f"Please log in and change your password as soon as possible.\n\n"
                    f"Login URL: https://yourapp.com/login\n\n"
                    f"Best regards,\n"
                    f"The FixMyHouse Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            return JsonResponse({'success': True, 'message': 'Team member invited successfully.'})

        except TeamMember.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Member not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)