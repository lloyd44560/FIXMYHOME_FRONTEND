from django.shortcuts import render, redirect,get_object_or_404
from datetime import datetime

from renter.models import Renter, ConditionReport, EmailVerification, FailedLoginAttempt, MinimumStandardReport
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from .forms import RenterForm
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
import json
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .forms import JobForm
from trader.models import Jobs
from agent.models.propertyAgent import Property
from agent.models.registerAgent import AgentRegister
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
import json
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponseNotAllowed

from renter.models import RenterRoom, RenterRoomAreaCondition, RoomApplianceReport
import traceback

def home(request):
    return render(request, 'renter/home.html')

def register(request):

    if request.method == 'POST':
        data = request.POST
        files = request.FILES

        if Renter.objects.filter(email=data.get('email')).exists():
            return render(request, 'renter/register.html',
            {'error': 'Email already registered.'})

        renter = Renter.objects.create(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            password=make_password(data.get('password')),

            company_name=data.get('company'),
            contact_person=data.get('contactPerson'),
            contact_person_email=data.get('contactPersonEmail'),
            contact_phone=data.get('contactPhone'),
            state=data.get('state'),
            city=data.get('city'),
            zip_code=data.get('zip'),
            company_address_line1=data.get('companyAddressLine1'),
            company_address_line2=data.get('companyAddressLine2'),
            company_postal_code=data.get('companyPostalCode'),
            upload_option=data.get('uploadOption'),
            property_image=files.get('propertyImage'),
            floor_count=data.get('floorCount') or None,
            room_count=data.get('roomCount') or None,
            address_line1=data.get('houseAddressLine1'),
            address_line2=data.get('houseAddressLine2'),
            house_state=data.get('houseState'),
            house_city=data.get('houseCity'),
            house_zip=data.get('houseZip'),
        )

        # return redirect('success')

    return render(request, 'renter/register.html')

def login_page(request):
    return render(request, 'renter/login.html')

def login_view(request):
    locked_until_str = request.session.get('locked_until')
    if locked_until_str:
        try:
            locked_until = timezone.datetime.fromisoformat(locked_until_str)
            if timezone.now() < locked_until:
                remaining_seconds = int((locked_until - timezone.now()).total_seconds())
                return render(request, 'renter/login.html', {
                    'error': 'Account temporarily locked.',
                    'lockout': True,
                    'remaining_seconds': remaining_seconds
                })
            else:
                request.session.pop('locked_until', None)
        except Exception as e:
            print("Error parsing lockout time:", e)
            traceback.print_exc()
            request.session.pop('locked_until', None)

    next_url = request.GET.get('next', '/welcome/')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        next_url = request.POST.get('next') or '/welcome/'

        try:
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                return render(request, 'renter/login.html', {
                    'error': 'No user found with this email.',
                    'next': next_url
                })

            fail_record, _ = FailedLoginAttempt.objects.get_or_create(user=user_obj)

            # Handle lockout
            if fail_record.is_locked and fail_record.locked_until and timezone.now() < fail_record.locked_until:
                request.session['locked_until'] = fail_record.locked_until.isoformat()
                remaining_seconds = int((fail_record.locked_until - timezone.now()).total_seconds())
                return render(request, 'renter/login.html', {
                    'error': 'Your account is temporarily locked.',
                    'lockout': True,
                    'remaining_seconds': remaining_seconds
                })
            elif fail_record.is_locked:
                fail_record.is_locked = False
                fail_record.attempts = 0
                fail_record.locked_until = None
                fail_record.save()

            # Try authentication
            user = authenticate(request, username=user_obj.username, password=password)

            if user:
                if not user.is_active:
                    return render(request, 'renter/login.html', {
                        'error': 'Your account is inactive. Please activate your email.',
                        'next': next_url
                    })

                renter_record = Renter.objects.filter(email=user_obj.email).first()

                login(request, user)
                fail_record.attempts = 0
                fail_record.save()
                request.session.pop('locked_until', None)

                # Set renter session details
                if renter_record:
                    request.session['renter_id'] = renter_record.id
                    request.session['renter_phone'] = renter_record.phone
                    request.session['renter_company'] = renter_record.company_name
                    request.session['renter_contact'] = renter_record.contact_person
                    request.session['renter_email'] = renter_record.email

                # Redirect based on role
                if user_obj.is_staff:
                    return redirect('/trader/home')
                elif user_obj.is_superuser:
                    return redirect('/agent/home')
                # elif ThirdParty.objects.filter(contact_email=user_obj.email).exists():
                #     return redirect('/third_party/home')
                else:
                    return redirect('/welcome/')

            else:
                fail_record.attempts += 1
                if fail_record.attempts >= 3:
                    fail_record.is_locked = True
                    fail_record.locked_until = timezone.now() + timedelta(minutes=5)
                    request.session['locked_until'] = fail_record.locked_until.isoformat()
                    fail_record.save()
                    return render(request, 'renter/login.html', {
                        'error': "Your account has been locked after 3 failed attempts. Please try again later.",
                        'lockout': True,
                        'remaining_seconds': 300
                    })

                fail_record.save()
                remaining = 3 - fail_record.attempts
                return render(request, 'renter/login.html', {
                    'error': f"Incorrect password. {remaining} attempt(s) remaining.",
                    'next': next_url
                })

        except Exception as e:
            print("Login Error:", e)
            traceback.print_exc()
            return render(request, 'renter/login.html', {
                'error': f'Unexpected error occurred: {str(e)}',
                'next': next_url
            })

    return render(request, 'renter/login.html', {'next': next_url})

# @csrf_exempt
# def register_renter(request):
#     if request.method == 'POST':
#         try:
#             # Get Personal Information
#             name = request.POST.get('name')
#             email = request.POST.get('email')
#             phone = request.POST.get('phone')
#             password = request.POST.get('password')
#             confirm_password = request.POST.get('confirmPassword')

#             company = request.POST.get('company')
#             contact_person = request.POST.get('contactPerson')
#             contact_email = request.POST.get('contactPersonEmail')
#             contact_phone = request.POST.get('contactPhone')

#             state = request.POST.get('state')
#             city = request.POST.get('city')
#             address1 = request.POST.get('companyAddressLine1')
#             address2 = request.POST.get('companyAddressLine2')
#             postal_code = request.POST.get('postalcode')

#             upload_option = request.POST.get('uploadOption')


#             condition_data = request.POST.get('conditionData')
#             condition_data_raw = request.POST.get('conditionData')
#             room_list_data = request.POST.get('roomListData')

#             property_image = None
#             uploaded_file_url = None

#             # if upload_option == 'manual':
#             #     property_image = request.FILES.get('propertyImage')
#             #     condition_image = request.FILES.get('conditionImage')

#             #     floor_count = request.POST.get('floorCount')
#             #     house_state = request.POST.get('houseState')
#             #     house_city = request.POST.get('houseCity')


#             #     if property_image:
#             #         fs = FileSystemStorage()
#             #         filename = fs.save(property_image.name, property_image)
#             #         uploaded_file_url = fs.url(filename)

#             # else:
#             #     condition_data = request.POST.get('conditionData')
#             #     condition_data_raw = request.POST.get('conditionData')
#             #     room_list_data = request.POST.get('roomListData')

#             # if password != confirm_password:
#             #     return redirect('/register?error=password-mismatch')

#             # Create User
#             user = User.objects.create_user(
#                 username=email,
#                 email=email,
#                 password=password,  # plain password; will be hashed internally
#                 # first_name=name
#             )

#             try:
#                 renter = Renter.objects.create(
#                     user=user,
#                     phone=phone,
#                     name=name,
#                     email=email,
#                     company_name=company,
#                     contact_person=contact_person,
#                     contact_phone=contact_phone,
#                     state=state,
#                     city=city,
#                     address_line1=address1,
#                     address_line2=address2,
#                 )
#             except Exception as e:
#                 print("Error creating renter:", e)
#                 return JsonResponse({"error": str(e)})
#             # # Create Property if manual
#             if upload_option == 'manual':
#                 property = Property.objects.create(
#                     renter=renter,
#                     floor_count=floor_count,
#                     state=house_state,
#                     city=house_city,
#                     address_line1=address1,
#                     address_line2=address2,
#                     postal_code=postal_code,
#                     property_photo=property_image,

#                     condition_report  = request.FILES.get('propertyFile')
#                 )
#             else:
#                 property = None

#             # # Save Room list


#             # if room_list_data:
#             #     room_names = json.loads(room_list_data)
#             #     for room_name in room_names:
#             #         Room.objects.create(property=property, room_name=room_name)
#             # property_image = request.FILES.get('propertyImage')
#             # condition_image = request.FILES.get('conditionImage')

#             # floor_count = request.POST.get('floorCount')
#             # house_state = request.POST.get('houseState')
#             # house_city = request.POST.get('houseCity')


#             # if property_image:
#             #     fs = FileSystemStorage()
#             #     filename = fs.save(property_image.name, property_image)
#             #     uploaded_file_url = fs.url(filename)

#             # property = Property.objects.create(
#             #         renter=renter,
#             #         floor_count=floor_count,
#             #         state=house_state,
#             #         city=house_city,
#             #         address_line1=address1,
#             #         address_line2=address2,
#             #         postal_code=postal_code,
#             #         property_photo=property_image,

#             #         condition_report  = request.FILES.get('propertyFile')
#             # )

#             # # Save Condition Report

#             # condition_data = request.POST.get('conditionData')
#             # condition_data_raw = request.POST.get('conditionData')
#             # room_list_data = request.POST.get('roomListData')

#             # if condition_data_raw:
#             #     try:
#             #         condition_data = json.loads(condition_data_raw)
#             #         extra = condition_data.get("extraInfo", {})
#             #         rooms = condition_data.get("rooms", [])

#             #         for index, room in enumerate(rooms):
#             #             room_name = room.get('categoryName', 'Unknown')
#             #             width = room.get('width', '')
#             #             length = room.get('length', '')
#             #             photo_field_name = f'room_photo_{index}'
#             #             photo = request.FILES.get(photo_field_name)

#             #             property_image = request.FILES.get('propertyImage')

#             #             room_condition = RoomCondition.objects.create(
#             #                 property=property,
#             #                 renter=renter,
#             #                 room_name=room_name,
#             #                 width=width,
#             #                 length=length,
#             #                 photo=photo,
#             #                 condition_report_date=extra.get('condition_report_date', ''),
#             #                 agreement_start_date=extra.get('agreement_start_date', ''),
#             #                 renter_received_date=extra.get('renter_received_date', ''),
#             #                 report_return_date=extra.get('report_return_date', ''),
#             #                 address=extra.get('address', ''),
#             #                 full_name_1=extra.get('full_name_1', ''),
#             #                 agent_name=extra.get('agent_name', ''),
#             #                 agent_company_name=extra.get('agent_company_name', ''),
#             #                 renter_1=extra.get('renter_1', ''),
#             #                 renter_2=extra.get('renter_2', '')
#             #             )

#             #             for area in room.get('areas', []):
#             #                 RoomAreaCondition.objects.create(
#             #                     room_condition=room_condition,
#             #                     area_name=area.get('areaName', ''),
#             #                     status=area.get('status', ''),
#             #                     renter_comment=area.get('renter_comment', '')
#             #                 )
#             #     except json.JSONDecodeError as e:
#             #         print("Failed to decode condition data JSON:", e)
#             # else:
#             #     print("Wala Condition Report")

#             # # Appliance Reports
#             # appliance_reports_data = request.POST.get('applianceReports')
#             # if appliance_reports_data:
#             #     try:
#             #         report_list = json.loads(appliance_reports_data)
#             #         for index, report in enumerate(report_list):
#             #             room_name = report.get('roomName')
#             #             room_obj, created = Room.objects.get_or_create(
#             #                 property=property,
#             #                 room_name=room_name,
#             #             )

#             #             # Handle appliance photo
#             #             photo_field_name = f'appliance_photo_{index}'
#             #             appliance_photo = request.FILES.get(f"appliance_photo_{index}")  # ← get image file

#             #             ApplianceReport.objects.create(
#             #                 room=room_obj,
#             #                 renter=renter,
#             #                 window_height=report.get('window_height'),
#             #                 window_length=report.get('window_length'),
#             #                 window_width=report.get('window_width'),
#             #                 brand=report.get('brand'),
#             #                 model_serial=report.get('model_serial'),
#             #                 location=report.get('location'),
#             #                 comments=report.get('comments'),
#             #                 appliance_photo=appliance_photo
#             #             )
#             #     except Exception as e:
#             #         print("Appliance report error:", e)

#             # # Minimum Standard Report
#             # standard_report_data = request.POST.get('standardReportData')
#             # standard_file = request.FILES.get('propertyFile')

#             # if standard_report_data:
#             #     try:
#             #         report = json.loads(standard_report_data)
#             #         MinimumStandardReport.objects.create(
#             #             renter=renter,
#             #             tenant_name=report.get('tenant_name'),
#             #             audit_no=report.get('audit_no'),
#             #             auditor=report.get('auditor'),
#             #             inspection_address=report.get('inspection_address'),
#             #             managing_agent=report.get('managing_agent'),
#             #             audit_date=report.get('audit_date'),
#             #             room=report.get('room'),
#             #             comments=report.get('comments'),
#             #             report_file=standard_file
#             #         )
#             #     except Exception as e:
#             #         print("Minimum standard error:", e)

#             # # Email verification
#             # ev = EmailVerification.objects.create(user=user)
#             # verify_url = request.build_absolute_uri(
#             #     reverse('verify_email', args=[str(ev.token)])
#             # )

#             # Uncomment when ready to send email and user will verify it
#             # send_mail(
#             #     subject="Please verify your email",
#             #     message=f"Hi {user.first_name},\n\nThanks for registering! Verify your email:\n{verify_url}",
#             #     from_email=settings.EMAIL_HOST_USER,
#             #     recipient_list=[user.email],
#             # )

#             return render(request, 'renter/verify_sent.html')

#         except Exception as e:
#             print("Registration error:", e)
#             return redirect('/register?error=internal')

#     else:
#         print("Form not submitted")
#         return redirect('/register')

# working
# @csrf_exempt
# def register_renter(request):

#     agents = AgentRegister.objects.all()
#     agent_id = request.POST.get('agent_id')
#     agent = AgentRegister.objects.get(id=agent_id) if agent_id else None
#     if request.method == 'POST':
#         try:
#             # Get Personal Information
#             name = request.POST.get('name')
#             email = request.POST.get('email')
#             phone = request.POST.get('phone')
#             password = request.POST.get('password')
#             confirm_password = request.POST.get('confirmPassword')

#             company = request.POST.get('company')
#             contact_person = request.POST.get('contactPerson')
#             contact_email = request.POST.get('contactPersonEmail')
#             contact_phone = request.POST.get('contactPhone')

#             state = request.POST.get('state')
#             city = request.POST.get('city')
#             address1 = request.POST.get('companyAddressLine1')
#             address2 = request.POST.get('companyAddressLine2')
#             postal_code = request.POST.get('postalcode')

#             upload_option = request.POST.get('uploadOption')

#             condition_data_raw = request.POST.get('conditionData')
#             room_list_data = request.POST.get('roomListData')
#             appliance_reports_data = request.POST.get('applianceReports')
#             standard_report_data = request.POST.get('standardReportData')


#             property_image = request.FILES.get('propertyImage')
#             condition_file = request.FILES.get('propertyFile')

#             if password != confirm_password:
#                 return JsonResponse({"error": "Passwords do not match."}, status=400)

#             # Create User
#             user = User.objects.create_user(
#                 username=email,
#                 email=email,
#                 password=password,
#                 is_active=False
#             )

#             # Create Renter
#             renter = Renter.objects.create(
#                 user=user,
#                 phone=phone,
#                 name=name,
#                 email=email,
#                 company_name=company,
#                 contact_person=contact_person,
#                 contact_person_email=contact_email,
#                 contact_phone=contact_phone,
#                 state=state,
#                 city=city,
#                 address_line1=address1,
#                 address_line2=address2,
#                 company_postal_code=postal_code,
#             )

#             # Create Property if manual
#             if upload_option == 'manual':

#                 floor_count = request.POST.get('floorCount_manual')
#                 house_state = request.POST.get('houseState')
#                 house_city = request.POST.get('houseCity')
#                 lease_start_manual = request.POST.get('leaseStart_manual')
#                 lease_end_manual = request.POST.get('leaseEnd_manual')
#                 # agent = AgentRegister.objects.get(id=agent_id) if agent_id else None
#                 property = Property.objects.create(
#                     renter=renter,
#                     floor_count=floor_count,
#                     state=house_state,
#                     city=house_city,
#                     address=address1,
#                     postal_code=postal_code,
#                     property_photo=property_image,
#                     condition_report=condition_file,
#                     lease_start=lease_start_manual,
#                     lease_end=lease_end_manual,
#                     agent=agent,  # required

#                 )
#             else:
#                 property = None


#                 # property = Property.objects.create(
#                 #     renter=renter,
#                 #     floor_count=floor_count,
#                 #     state=house_state,
#                 #     city=house_city,
#                 #     address=address1,
#                 #     # address_line2=address2,
#                 #     postal_code=postal_code,
#                 #     property_photo=property_image,
#                 #     condition_report=condition_file
#                 # )


#                 # # Save Room list
#                 # if room_list_data and property:
#                 #     try:
#                 #         room_names = json.loads(room_list_data)
#                 #         for room_name in room_names:
#                 #             Room.objects.create(property=property, room_name=room_name)
#                 #     except json.JSONDecodeError as e:
#                 #         print("Room list error:", e)

#                 # # Save Condition Report
#                 # if condition_data_raw and property:
#                 #     try:
#                 #         condition_data = json.loads(condition_data_raw)
#                 #         extra = condition_data.get("extraInfo", {})
#                 #         rooms = condition_data.get("rooms", [])

#                 #         for index, room in enumerate(rooms):
#                 #             photo = request.FILES.get(f'room_photo_{index}')
#                 #             room_condition = RoomCondition.objects.create(
#                 #                 property=property,
#                 #                 renter=renter,
#                 #                 room_name=room.get('categoryName', 'Unknown'),
#                 #                 width=room.get('width', ''),
#                 #                 length=room.get('length', ''),
#                 #                 photo=photo,
#                 #                 condition_report_date=extra.get('condition_report_date', ''),
#                 #                 agreement_start_date=extra.get('agreement_start_date', ''),
#                 #                 renter_received_date=extra.get('renter_received_date', ''),
#                 #                 report_return_date=extra.get('report_return_date', ''),
#                 #                 address=extra.get('address', ''),
#                 #                 full_name_1=extra.get('full_name_1', ''),
#                 #                 agent_name=extra.get('agent_name', ''),
#                 #                 agent_company_name=extra.get('agent_company_name', ''),
#                 #                 renter_1=extra.get('renter_1', ''),
#                 #                 renter_2=extra.get('renter_2', '')
#                 #             )
#                 #             for area in room.get('areas', []):
#                 #                 RoomAreaCondition.objects.create(
#                 #                     room_condition=room_condition,
#                 #                     area_name=area.get('areaName', ''),
#                 #                     status=area.get('status', ''),
#                 #                     renter_comment=area.get('renter_comment', '')
#                 #                 )
#                 #     except json.JSONDecodeError as e:
#                 #         print("Condition report error:", e)

#                 # # Save Appliance Reports
#                 # if appliance_reports_data and property:
#                 #     try:
#                 #         reports = json.loads(appliance_reports_data)
#                 #         for index, report in enumerate(reports):
#                 #             photo = request.FILES.get(f"appliance_photo_{index}")
#                 #             room_name = report.get("roomName")
#                 #             room_obj, _ = Room.objects.get_or_create(property=property, room_name=room_name)

#                 #             ApplianceReport.objects.create(
#                 #                 room=room_obj,
#                 #                 renter=renter,
#                 #                 window_height=report.get("window_height"),
#                 #                 window_length=report.get("window_length"),
#                 #                 window_width=report.get("window_width"),
#                 #                 brand=report.get("brand"),
#                 #                 model_serial=report.get("model_serial"),
#                 #                 location=report.get("location"),
#                 #                 comments=report.get("comments"),
#                 #                 appliance_photo=photo
#                 #             )
#                 #     except Exception as e:
#                 #         print("Appliance report error:", e)

#                 # # Save Minimum Standard Report
#                 # if standard_report_data:
#                 #     try:
#                 #         report = json.loads(standard_report_data)
#                 #         MinimumStandardReport.objects.create(
#                 #             renter=renter,
#                 #             tenant_name=report.get("tenant_name"),
#                 #             audit_no=report.get("audit_no"),
#                 #             auditor=report.get("auditor"),
#                 #             inspection_address=report.get("inspection_address"),
#                 #             managing_agent=report.get("managing_agent"),
#                 #             audit_date=report.get("audit_date"),
#                 #             room=report.get("room"),
#                 #             comments=report.get("comments"),
#                 #             report_file=condition_file
#                 #         )


#                 #     except Exception as e:
#                 #         print("Minimum standard error:", e)

#             ev = EmailVerification.objects.create(user=user)
#             verify_url = request.build_absolute_uri(
#                 reverse('verify_email', args=[str(ev.token)])
#             )

#             send_mail(
#                 subject="Please verify your email",
#                 message=f"Hi {name},\n\nThanks for registering! Please verify your email by clicking the link below:\n\n{verify_url}",
#                 from_email=settings.EMAIL_HOST_USER,
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )
#             agents = AgentRegister.objects.all()
#             return render(request, 'renter/register.html', {
#                 'agents': agents
#             })

#         except Exception as e:
#             print("Registration error:", e)
#             return JsonResponse({"error": str(e)}, status=500)
#     else:
#         agents = AgentRegister.objects.all()
#         return render(request, 'renter/register.html', {
#             'agents': agents
#         })

#     return JsonResponse({"error": "Invalid request method."}, status=405)


def json_error(message, status=400):
    return JsonResponse({"error": message}, status=status)

@csrf_exempt
def register_renter(request):
    agents = AgentRegister.objects.all()

    if request.method == 'GET':
        return render(request, 'renter/register.html', {
            'agents': agents
        })

    elif request.method == 'POST':
        try:
            # 1. Personal Info
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirmPassword')

            if not all([name, email, phone, password, confirm_password]):
                return json_error("All personal fields are required.")

            if password != confirm_password:
                return json_error("Passwords do not match.")

            if User.objects.filter(username=email).exists():
                return json_error("Email is already registered.")

            # 2. Company Info
            company = request.POST.get('company')
            contact_person = request.POST.get('contactPerson')
            contact_email = request.POST.get('contactPersonEmail')
            contact_phone = request.POST.get('contactPhone')

            state = request.POST.get('state')
            city = request.POST.get('city')
            address1 = request.POST.get('companyAddressLine1')
            address2 = request.POST.get('companyAddressLine2')
            postal_code = request.POST.get('postalcode')

            if not all([company, contact_person, contact_email, contact_phone]):
                return json_error("All company fields are required.")

            # 3. Create user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_active=False
            )

            # 4. Create Renter
            renter = Renter.objects.create(
                user=user,
                phone=phone,
                name=name,
                email=email,
                company_name=company,
                contact_person=contact_person,
                contact_person_email=contact_email,
                contact_phone=contact_phone,
                state=state,
                city=city,
                address_line1=address1,
                address_line2=address2,
                company_postal_code=postal_code,
            )

            # 5. Property Handling
            upload_option = request.POST.get('uploadOption')
            agent_id = request.POST.get('agent_id')
            try:
                agent = AgentRegister.objects.get(id=agent_id) if agent_id else None
            except AgentRegister.DoesNotExist:
                return json_error("Agent not found.")

            if upload_option == 'manual':
                floor_count = request.POST.get('floorCount_manual')
                lease_start = request.POST.get('leaseStart_manual')
                lease_end = request.POST.get('leaseEnd_manual')
                house_state = request.POST.get('houseState_manual')
                house_city = request.POST.get('houseCity_manual')
                property_image = request.FILES.get('propertyImage')
                condition_file = request.FILES.get('propertyFile')

                missing_fields = []
                if not floor_count:
                    missing_fields.append("floorCount_manual")
                if not lease_start:
                    missing_fields.append("leaseStart_manual")
                if not lease_end:
                    missing_fields.append("leaseEnd_manual")
                if not house_state:
                    missing_fields.append("houseState_manual")
                if not house_city:
                    missing_fields.append("houseCity_manual")

                if missing_fields:
                    return json_error(f"The following fields are missing or empty: {', '.join(missing_fields)}")

                # if not all([floor_count, lease_start, lease_end, house_state, house_city]):
                #     return json_error("All manual property fields are required.")

                property = Property.objects.create(
                    renter=renter,
                    floor_count=floor_count,
                    state=house_state,
                    city=house_city,
                    address=address1,
                    postal_code=postal_code,
                    property_photo=property_image,
                    condition_report=condition_file,
                    lease_start=lease_start,
                    lease_end=lease_end,
                    agent=agent,
                )
            else:

                # Create Property from modal fields
                floor_count = request.POST.get('floorCount')
                lease_start = request.POST.get('lease_start')
                lease_end = request.POST.get('lease_end')
                house_state = request.POST.get('houseState')
                house_city = request.POST.get('houseCity')
                address = request.POST.get('propertyAddress')
                postal_code = request.POST.get('propertyPostalCode')
                property_image = request.FILES.get('propertyImage')
                condition_file = request.FILES.get('propertyFile')

                property = Property.objects.create(
                    renter=renter,
                    floor_count=floor_count,
                    lease_start=lease_start,
                    lease_end=lease_end,
                    state=house_state,
                    city=house_city,
                    address=address,
                    postal_code=postal_code,
                    property_photo=property_image,
                    condition_report=condition_file,
                    agent=agent,
                )

                # Now create Room
                room_name = request.POST.get('roomName')
                room_floor = request.POST.get('roomFloor')
                room = RenterRoom.objects.create(
                    renter=renter,
                    property=property,
                    room_name=room_name,
                    # floor_level=room_floor


                )

                # Now create RoomAreaCondition(s)
                area_names = request.POST.getlist('area_name[]')
                conditions = request.POST.getlist('condition[]')
                remarks = request.POST.getlist('remarks[]')

                for name, cond, remark in zip(area_names, conditions, remarks):
                    RenterRoomAreaCondition.objects.create(
                        room=room,
                        area_name=name,
                        status=cond,
                        remarks=remark
                    )

                property = None  # For now you’re skipping automatic upload handling
                # Collect lahat ng laman ng section para sa Property record creation
                # Collect lahat ng section para sa RenterRoom record creation
                # Collect lahat ng section para sa RenterRoomAreaCondition
                # then isave pag valid lahat


            # 6. Email verification
            ev = EmailVerification.objects.create(user=user)
            verify_url = request.build_absolute_uri(
                reverse('verify_email', args=[str(ev.token)])
            )

            send_mail(
                subject="Please verify your email",
                message=f"Hi {name},\n\nThanks for registering! Please verify your email by clicking the link below:\n\n{verify_url}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return render(request, 'renter/verify_sent.html')
            # return JsonResponse({
            #     "success": True,
            #     "message": "Renter registered successfully. Please verify your email.",
            # })

        except Exception as e:
            traceback.print_exc()
            return json_error(str(e), status=500)

    # Default fallback for unsupported methods
    return json_error("Invalid request method.", status=405)

# def register_renter(request):
#     if request.method == 'POST':
#         form = RenterForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('success_page')  # replace with your success redirect
#     else:
#         form = RenterForm()
#     return render(request, 'register.html', {'form': form})

def verify_email(request, token):
    try:
        ev = EmailVerification.objects.get(token=token)
    except EmailVerification.DoesNotExist:
        # Token not found or already used
        return render(request, 'renter/verify_invalid.html')

    # If token expired (>24h), delete it and show expired page
    if timezone.now() > ev.created_at + timedelta(hours=24):
        ev.delete()
        return render(request, 'renter/verify_expired.html')

    # Otherwise activate the user
    user = ev.user
    user.is_active = True
    user.save()
    ev.delete()  # one-time use

    return render(request, 'renter/verified.html', {'user': user})


@login_required
def welcome(request):
    user = request.user

    try:
        if Renter.objects.filter(user=user).exists():
            renter = Renter.objects.get(user=user)
            properties = Property.objects.filter(renter=renter)
            room_conditions = RoomCondition.objects.filter(renter=renter).prefetch_related('areas')
            appliance_reports = ApplianceReport.objects.filter(renter=renter).select_related('room', 'renter')
            minimum_reports = MinimumStandardReport.objects.filter(renter=renter)
            job_list = Jobs.objects.filter(renter=renter)
            agents = AgentRegister.objects.all()

            return render(request, 'renter/welcome.html', {
                'renter': renter,
                'renter_id': renter.id,
                'room_conditions': room_conditions,
                'properties': properties,
                'appliance_reports': appliance_reports,
                'minimum_reports': minimum_reports,  # ✅ fixed name
                'jobs': job_list,
                'job_form': JobForm(),
                'agents': agents,
            })

        elif ThirdParty.objects.filter(user=user).exists():
            return redirect('thirdparty_account')

        else:
            return render(request, 'renter/welcome.html', {
                'renter': None,
                'renter_id': None,
                'room_conditions': [],
                'properties': [],
                'appliance_reports': [],
                'minimum_reports': [],  # ✅ fix name here too
                'jobs': [],
                'job_form': JobForm(),
                'agents': [],
            })

    except Exception as e:
        print("Welcome view error:", e)
        return render(request, 'renter/welcome.html', {
            'renter': None,
            'renter_id': None,
            'room_conditions': [],
            'properties': [],
            'appliance_reports': [],
            'minimum_reports': [],  # ✅ fix in error fallback too
            'jobs': [],
            'job_form': JobForm(),
            'agents': [],
        })



def renter_create(request):
    if request.method == 'POST':
        form = RenterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = RenterForm()
    return render(request, 'renter_form.html', {'form': form})


def send_reset_link(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # You can later validate if the email exists in your database.
            subject = 'Password Reset Link'
            message = 'Here is your password reset link: http://example.com/reset-password/'
            from_email = 'wsi.jborlagdan@gmail.com'
            recipient_list = [email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, 'Password reset link sent to your email.')
                print("Email is sent")
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
                print(request, f'Error sending email: {str(e)}')
        else:
            messages.error(request, 'Please enter your email address.')

    return redirect('/login_renter/')  # Adjust to your login page URL

@login_required
def renter_account(request):
    user = request.user
    renter = get_object_or_404(Renter, user=user)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        pin = request.POST.get('pin', '')
        gender = request.POST.get('gender', '')
        dob = request.POST.get('dob', '')
        address_line1 = request.POST.get('address_line1', '')
        address_line2 = request.POST.get('address_line2', '')

        # Update user fields
        if name:
            split_name = name.split()
            user.first_name = split_name[0]
            user.last_name = ' '.join(split_name[1:]) if len(split_name) > 1 else ''
        if email:
            user.email = email
        user.save()

        # Update renter fields
        renter.phone = phone
        renter.gender = gender
        renter.date_of_birth = dob or None
        renter.address_line1 = address_line1
        renter.address_line2 = address_line2
        renter.save()

        # #  Update related Property records
        # Property.objects.filter(renter=renter).update(
        #     address_line1=address_line1,
        #     address_line2=address_line2
        # )

        messages.success(request, 'Account updated successfully.')
        return redirect('renter_account')

    return render(request, 'renter/home/account.html', {
        'user': user,
        'renter': renter
    })


def chat_demo(request, job_id):
    return render(request, 'chat_demo.html', {'job_id': job_id})

def demo_chat(request):
    chats = [
        {'image': 'images/user1.jpg', 'job_number': 'QOT-0000391', 'message': 'Good afternoon, I will be...', 'distance': '25m away'},
        {'image': 'images/user2.jpg', 'job_number': 'QOT-0000392', 'message': 'How was the repair? Did...', 'distance': '33m away'},
        {'image': 'images/user3.jpg', 'job_number': 'QOT-0000393', 'message': 'No worries. Let me know...', 'distance': '2km away'},
        {'image': 'images/user4.jpg', 'job_number': 'QOT-0000394', 'message': 'I’m checking if I have the...', 'distance': '2.5km away'},
        {'image': 'images/user5.jpg', 'job_number': 'QOT-0000395', 'message': 'I will need your confirma...', 'distance': '2.8km away'},
    ]
    return render(request, 'renter/home/messages.html', {'chats': chats})

def demo_chat(request):
    chats = [
        {'image': 'images/user1.jpg', 'job_number': 'QOT-0000391', 'message': 'Good afternoon, I will be...', 'distance': '25m away'},
        {'image': 'images/user2.jpg', 'job_number': 'QOT-0000392', 'message': 'How was the repair? Did...', 'distance': '33m away'},
        {'image': 'images/user3.jpg', 'job_number': 'QOT-0000393', 'message': 'No worries. Let me know...', 'distance': '2km away'},
    ]
    return render(request, 'renter/home/messages.html', {'chats': chats})

def chat_thread(request, job_number):
    # Dummy messages for the thread
    messages = [
        {'sender': 'Lucas', 'message': 'Hi Brooke!', 'is_sender': False},
        {'sender': 'Lucas', 'message': "It's going well. Thanks for asking!", 'is_sender': False},
        {'sender': 'You', 'message': "No worries. Let me know if you need any help 😉", 'is_sender': True},
    ]
    return render(request, 'renter/home/chat_thread.html', {'job_number': job_number, 'messages': messages})

def login_error(request):
    return render(request, 'renter/login_error.html')


def custom_logout(request):
    # Check if the user logged in via Google
    if request.user.social_auth.filter(provider='google-oauth2').exists():
        logout(request)  # End Django session
        return redirect('https://accounts.google.com/Logout?continue=https://sandbox.fixmh.com/login_renter/')
    else:
        logout(request)  # End Django session
        return redirect('/login_renter/')

@login_required
def add_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.renter = Renter.objects.get(user=request.user)
            job.save()
    return redirect('welcome')

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Jobs, id=job_id)
    if job.renter.user == request.user:
        job.delete()
    return redirect('welcome')


@login_required
def edit_job(request):
    if request.method == "POST":
        job_id = request.POST.get("job_id")
        job = get_object_or_404(Jobs, id=job_id)

        priority = request.POST.get("priority") == "true"
        status = request.POST.get("status")

        job.priority = priority
        job.status = status
        job.notes = request.POST.get("notes", "")
        job.save()

        return redirect('welcome')  # update to your actual name

@login_required
def edit_room_condition_json(request, pk):
    try:
        room = RoomCondition.objects.get(pk=pk, renter=request.user.renter)

        area_data = []
        for area in room.areas.all():
            area_data.append({
                "id": area.id,
                "area_name": area.area_name,
                "status": area.status,
            })

        condition_date = room.condition_report_date
        if isinstance(condition_date, str):
            date_str = condition_date
        else:
            date_str = condition_date.strftime('%Y-%m-%d') if condition_date else ''

        return JsonResponse({
            'id': room.id,
            'room_name': room.room_name,
            'agent_name': room.agent_name,
            'condition_report_date': date_str,
            'areas': area_data,
        })

    except Exception as e:
        import traceback
        print("Error in edit_room_condition_json:", e)
        traceback.print_exc()
        return JsonResponse({'error': 'Something went wrong'}, status=500)



@login_required
def update_room_condition(request):
    room_id = request.POST.get('room_condition_id')
    room = get_object_or_404(RoomCondition, pk=room_id, renter=request.user.renter)

    room.room_name = request.POST.get('room_name')
    room.agent_name = request.POST.get('agent_name')
    room.condition_report_date = request.POST.get('condition_report_date')
    room.save()

    # Update each area's status
    for area in room.areas.all():
        status_key = f"area_status_{area.id}"
        if status_key in request.POST:
            area.status = request.POST.get(status_key)
            area.save()

    return JsonResponse({"success": True})


@login_required
def get_appliance_report_json(request, pk):
    report = get_object_or_404(ApplianceReport, pk=pk, renter=request.user.renter)
    return JsonResponse({
        'id': report.id,
        'brand': report.brand,
        'model_serial': report.model_serial,
        'window_height': report.window_height,
        'window_length': report.window_length,
        'window_width': report.window_width,
        'location': report.location,
        'comments': report.comments or '',
    })

@require_POST
@login_required
def update_appliance_report(request):
    report_id = request.POST.get("appliance_report_id")
    report = get_object_or_404(ApplianceReport, pk=report_id, renter=request.user.renter)

    report.brand = request.POST.get("brand")
    report.model_serial = request.POST.get("model_serial")
    report.window_height = request.POST.get("window_height")
    report.window_length = request.POST.get("window_length")
    report.window_width = request.POST.get("window_width")
    report.location = request.POST.get("location")
    report.comments = request.POST.get("comments")
    report.save()

    return JsonResponse({'success': True})





@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')

        if len(new_password) < 8:
            messages.error(request, 'New password must be at least 8 characters.')
            return redirect('change_password')

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Keep user logged in
        messages.success(request, 'Password changed successfully.')
        return redirect('change_password')

    return render(request, 'renter/home/change_password.html')


# @login_required
# @csrf_exempt
# def add_property(request):
#     if request.method == 'POST':
#         user = request.user
#         try:
#             renter = Renter.objects.get(user=user)
#             agent_id = request.POST.get('agent_id')  #
#             agent = AgentRegister.objects.get(id=agent_id)

#             data = request.POST
#             property_photo = request.FILES.get('property_photo')
#             condition_report = request.FILES.get('condition_report')

#             prop = Property.objects.create(
#                 renter=renter,
#                 agent=agent,  # ✅assign agent
#                 name=data.get('name'),
#                 floor_count=data.get('floor_count'),
#                 city=data.get('city'),
#                 state=data.get('state'),
#                 address=data.get('address'),
#                 renter_name=data.get('renter_name'),
#                 renter_contact=data.get('renter_contact'),
#                 rent=data.get('rent'),
#                 postal_code=data.get('postal_code'),
#                 lease_start=data.get('lease_start'),
#                 lease_end=data.get('lease_end'),
#                 status=data.get('status'),
#                 property_photo=property_photo,
#                 condition_report=condition_report,
#             )

#             # return JsonResponse({
#             #     'success': True,
#             #     'message': 'Property added successfully.',
#             #     'property_id': prop.id,
#             #     'property_name': prop.name
#             # })

#             return redirect('/welcome/')

#         except Exception as e:
#             print("Error adding property:", e)
#             return JsonResponse({
#                 'success': False,
#                 'message': str(e)
#             }, status=500)



#     return JsonResponse({
#         'success': False,
#         'message': 'Only POST method allowed.'
#     }, status=405)


# @login_required
# def delete_property(request, id):
#     user = request.user
#     try:
#         renter = Renter.objects.get(user=user)
#         prop = get_object_or_404(Property, id=id, renter=renter)
#         prop.delete()
#     except Exception as e:
#         print("Error deleting property:", e)
#     return redirect('/welcome/')



# @login_required
# def unlink_property(request, id):
#     user = request.user
#     try:
#         renter = Renter.objects.get(user=user)
#         prop = get_object_or_404(Property, id=id, renter=renter)
#         prop.renter = None  #  unlink
#         prop.save()
#         return redirect('renter_welcome')
#     except Exception as e:
#         print("Unlink error:", e)
#         return redirect



# @login_required
# def edit_property(request, id):
#     if request.method == 'POST':
#         try:
#             prop = get_object_or_404(Property, id=id, renter__user=request.user)

#             data = request.POST
#             property_photo = request.FILES.get('property_photo')
#             condition_report = request.FILES.get('condition_report')

#             # Handle date fields safely
#             lease_start = data.get('lease_start') or None
#             lease_end = data.get('lease_end') or None
#             lease_start = datetime.strptime(lease_start, "%Y-%m-%d").date() if lease_start else None
#             lease_end = datetime.strptime(lease_end, "%Y-%m-%d").date() if lease_end else None

#             # Update fields
#             prop.name = data.get('name')
#             prop.floor_count = data.get('floor_count')
#             prop.city = data.get('city')
#             prop.state = data.get('state')
#             prop.address = data.get('address')
#             prop.renter_name = data.get('renter_name')
#             prop.renter_contact = data.get('renter_contact')
#             prop.rent = data.get('rent')
#             prop.postal_code = data.get('postal_code')
#             prop.lease_start = lease_start
#             prop.lease_end = lease_end
#             prop.status = data.get('status')
#             agent_id = data.get('agent_id')
#             if agent_id:
#                 prop.agent_id = agent_id

#             if property_photo:
#                 prop.property_photo = property_photo
#             if condition_report:
#                 prop.condition_report = condition_report

#             prop.save()

#             return JsonResponse({"success": True, "message": "Property updated successfully"})

#         except Exception as e:
#             print("Error updating property:", e)
#             return JsonResponse({"success": False, "message": str(e)})

#     return JsonResponse({"success": False, "message": "Invalid request method"})





# For Minimum STandard Reports


@login_required
def add_standard_report(request):
    if request.method == 'POST':
        try:
            renter = Renter.objects.get(user=request.user)
            MinimumStandardReport.objects.create(
                renter=renter,
                tenant_name=request.POST.get('tenant_name'),
                audit_no=request.POST.get('audit_no'),
                auditor=request.POST.get('auditor'),
                inspection_address=request.POST.get('inspection_address'),
                managing_agent=request.POST.get('managing_agent'),
                audit_date=request.POST.get('audit_date'),
                room=request.POST.get('room'),
                comments=request.POST.get('comments'),
                report_file=request.FILES.get('report_file')
            )
        except Exception as e:
            print("Add report error:", e)
    return redirect('/welcome/')


@login_required
def edit_standard_report(request, id):
    report = get_object_or_404(MinimumStandardReport, id=id, renter__user=request.user)
    if request.method == 'POST':
        try:
            report.tenant_name = request.POST.get('tenant_name')
            report.audit_no = request.POST.get('audit_no')
            report.auditor = request.POST.get('auditor')
            report.inspection_address = request.POST.get('inspection_address')
            report.managing_agent = request.POST.get('managing_agent')
            report.audit_date = request.POST.get('audit_date')
            report.room = request.POST.get('room')
            report.comments = request.POST.get('comments')
            file = request.FILES.get('report_file')
            if file:
                report.report_file = file
            report.save()
        except Exception as e:
            print("Edit report error:", e)
    return redirect('/welcome/')


@login_required
def delete_standard_report(request, id):
    try:
        report = get_object_or_404(MinimumStandardReport, id=id, renter__user=request.user)
        report.delete()
    except Exception as e:
        print("Delete report error:", e)
    return redirect('/welcome/')


@login_required
def condition_report_view(request):
    return render(request, 'renter/home/condition_reports/condition_report_modal.html')


@csrf_exempt
@login_required
def save_condition_report_all(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        renter = request.user.renter

        # Save property
        prop = Property.objects.create(
            renter=renter,
            name=data['property']['name'],
            address=data['property']['address'],
            location=data['property']['location']
        )

        # Save rooms
        for room_data in data['rooms']:
            room = RenterRoom.objects.create(
                renter=renter,
                property=prop,
                name=room_data['name'],
                type=room_data['type'],
            )

            # Save room area conditions
            for area in room_data['areas']:
                RoomAreaCondition.objects.create(
                    room=room,
                    area_name=area['area_name'],
                    condition=area['condition'],
                    remarks=area['remarks']
                )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'invalid'}, status=400)

