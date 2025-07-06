from django.shortcuts import render, redirect

from renter.models import Renter, Property, ApplianceReport, Room, ConditionReport, RoomCondition, RoomAreaCondition,EmailVerification, FailedLoginAttempt, MinimumStandardReport
from thirdparty.models import ThirdParty
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

User = get_user_model()

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

    next_url = request.GET.get('next', '/welcome/')
    
    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')
        next_url = request.POST.get('next') or '/welcome/'

        try:
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                return render(request, 'renter/login.html', {
                    'error': 'User with this email does not exist.',
                    'next': next_url
                })

            fail_record, _ = FailedLoginAttempt.objects.get_or_create(user=user_obj)

            if fail_record.is_locked and fail_record.locked_until and timezone.now() < fail_record.locked_until:
                request.session['locked_until'] = fail_record.locked_until.isoformat()
                remaining_seconds = int((fail_record.locked_until - timezone.now()).total_seconds())
                return render(request, 'renter/login.html', {
                    'error': 'Account temporarily locked.',
                    'lockout': True,
                    'remaining_seconds': remaining_seconds
                })
            elif fail_record.is_locked:
                fail_record.is_locked = False
                fail_record.attempts = 0
                fail_record.locked_until = None
                fail_record.save()

            user = authenticate(request, username=user_obj.username, password=password)

            if user:
                renter_record = Renter.objects.filter(email=user_obj.email).first()

                login(request, user)
                fail_record.attempts = 0
                fail_record.save()
                request.session.pop('locked_until', None)

                # Optional: Pass renter id to session if needed later
                if renter_record:
                    request.session['renter_id'] = renter_record.id
                    request.session['renter_id'] = renter_record.id
                    request.session['renter_phone'] = renter_record.phone
                    request.session['renter_company'] = renter_record.company_name
                    request.session['renter_contact'] = renter_record.contact_person
                    request.session['renter_email'] = renter_record.email


                if user_obj.is_staff:
                    return redirect('/trader/home')
                elif user_obj.is_superuser:
                    return redirect('/agent/home')
                # if found in 3rd party table redirect to ('third_party/home')
                elif ThirdParty.objects.filter(contact_email=user_obj.email).exists():
                    return redirect('/third_party/home')
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
                        'error': "Your account is now locked due to too many failed login attempts.",
                        'lockout': True,
                        'remaining_seconds': 300
                    })
                fail_record.save()
                remaining = 3 - fail_record.attempts
                return render(request, 'renter/login.html', {
                    'error': f"Incorrect password. {remaining} attempt(s) left.",
                    'next': next_url
                })

        except Exception as e:
            print("Login error:", e)
            return render(request, 'renter/login.html', {
                'error': 'An unexpected error occurred.',
                'next': next_url
            })

    return render(request, 'renter/login.html', {'next': next_url})

@csrf_exempt
def register_renter(request):
    if request.method == 'POST':
        try:
            # Get Personal Information
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirmPassword')

            company = request.POST.get('company')
            contact_person = request.POST.get('contactPerson')
            contact_email = request.POST.get('contactPersonEmail')
            contact_phone = request.POST.get('contactPhone')

            state = request.POST.get('state')
            city = request.POST.get('city')
            address1 = request.POST.get('companyAddressLine1')
            address2 = request.POST.get('companyAddressLine2')
            postal_code = request.POST.get('postalcode')

            upload_option = request.POST.get('uploadOption')

            property_image = None
            uploaded_file_url = None

            if upload_option == 'manual':
                property_image = request.FILES.get('propertyImage')
                condition_image = request.FILES.get('conditionImage')

                floor_count = request.POST.get('floorCount')
                house_state = request.POST.get('houseState')
                house_city = request.POST.get('houseCity')
             

                if property_image:
                    fs = FileSystemStorage()
                    filename = fs.save(property_image.name, property_image)
                    uploaded_file_url = fs.url(filename)

            else:
                condition_data = request.POST.get('conditionData')
                condition_data_raw = request.POST.get('conditionData')
                room_list_data = request.POST.get('roomListData')

            if password != confirm_password:
                return redirect('/register?error=password-mismatch')

            # Create User
            user = User.objects.create(
                username=email,
                email=email,
                password=make_password(password),
                first_name=name
            )

            # Create Renter
            renter = Renter.objects.create(
                user=user,
                phone=phone,
                name=name,
                email=email,
                company_name=company,
                contact_person=contact_person,
                contact_phone=contact_phone,
                state=state,
                city=city,
                address_line1=address1,
                address_line2=address2,
                upload_option=upload_option,
                property_image=uploaded_file_url,
            )

            # Create Property if manual
            if upload_option == 'manual':
                property = Property.objects.create(
                    renter=renter,
                    floor_count=floor_count,
                    state=house_state,
                    city=house_city,
                    address_line1=address1,
                    address_line2=address2,
                    postal_code=postal_code,
                    property_photo=property_image,
                    condition_report=condition_image
                )
            else:
                property = None

            # Save Room list

            
            # if room_list_data:
            #     room_names = json.loads(room_list_data)
            #     for room_name in room_names:
            #         Room.objects.create(property=property, room_name=room_name)
            property_image = request.FILES.get('propertyImage')
            condition_image = request.FILES.get('conditionImage')

            floor_count = request.POST.get('floorCount')
            house_state = request.POST.get('houseState')
            house_city = request.POST.get('houseCity')
            

            if property_image:
                fs = FileSystemStorage()
                filename = fs.save(property_image.name, property_image)
                uploaded_file_url = fs.url(filename)

            property = Property.objects.create(
                    renter=renter,
                    floor_count=floor_count,
                    state=house_state,
                    city=house_city,
                    address_line1=address1,
                    address_line2=address2,
                    postal_code=postal_code,
                    property_photo=property_image,
                    condition_report=condition_image
            )

            # Save Condition Report
            if condition_data_raw:
                try:
                    condition_data = json.loads(condition_data_raw)
                    extra = condition_data.get("extraInfo", {})
                    rooms = condition_data.get("rooms", [])

                    for index, room in enumerate(rooms):
                        room_name = room.get('categoryName', 'Unknown')
                        width = room.get('width', '')
                        length = room.get('length', '')
                        photo_field_name = f'room_photo_{index}'
                        photo = request.FILES.get(photo_field_name)

                        property_image = request.FILES.get('propertyImage')

                        room_condition = RoomCondition.objects.create(
                            property=property,
                            renter=renter,
                            room_name=room_name,
                            width=width,
                            length=length,
                            photo=photo,
                            condition_report_date=extra.get('condition_report_date', ''),
                            agreement_start_date=extra.get('agreement_start_date', ''),
                            renter_received_date=extra.get('renter_received_date', ''),
                            report_return_date=extra.get('report_return_date', ''),
                            address=extra.get('address', ''),
                            full_name_1=extra.get('full_name_1', ''),
                            agent_name=extra.get('agent_name', ''),
                            agent_company_name=extra.get('agent_company_name', ''),
                            renter_1=extra.get('renter_1', ''),
                            renter_2=extra.get('renter_2', '')
                        )

                        for area in room.get('areas', []):
                            RoomAreaCondition.objects.create(
                                room_condition=room_condition,
                                area_name=area.get('areaName', ''),
                                status=area.get('status', ''),
                                renter_comment=area.get('renter_comment', '')
                            )
                except json.JSONDecodeError as e:
                    print("Failed to decode condition data JSON:", e)

                    # Appliance Reports
            # Appliance Reports
            appliance_reports_data = request.POST.get('applianceReports')
            if appliance_reports_data:
                try:
                    report_list = json.loads(appliance_reports_data)
                    for index, report in enumerate(report_list):
                        room_name = report.get('roomName')
                        room_obj, created = Room.objects.get_or_create(
                            property=property,
                            room_name=room_name,
                        )

                        # Handle appliance photo
                        photo_field_name = f'appliance_photo_{index}'
                        appliance_photo = request.FILES.get(f"appliance_photo_{index}")  # ← get image file

                        ApplianceReport.objects.create(
                            room=room_obj,
                            renter=renter,
                            window_height=report.get('window_height'),
                            window_length=report.get('window_length'),
                            window_width=report.get('window_width'),
                            brand=report.get('brand'),
                            model_serial=report.get('model_serial'),
                            location=report.get('location'),
                            comments=report.get('comments'),
                            appliance_photo=appliance_photo
                        )
                except Exception as e:
                    print("Appliance report error:", e)

            # Minimum Standard Report
            standard_report_data = request.POST.get('standardReportData')
            standard_file = request.FILES.get('propertyFile')

            if standard_report_data:
                try:
                    report = json.loads(standard_report_data)
                    MinimumStandardReport.objects.create(
                        renter=renter,
                        tenant_name=report.get('tenant_name'),
                        audit_no=report.get('audit_no'),
                        auditor=report.get('auditor'),
                        inspection_address=report.get('inspection_address'),
                        managing_agent=report.get('managing_agent'),
                        audit_date=report.get('audit_date'),
                        room=report.get('room'),
                        comments=report.get('comments'),
                        report_file=standard_file
                    )
                except Exception as e:
                    print("Minimum standard error:", e)

            # Email verification
            ev = EmailVerification.objects.create(user=user)
            verify_url = request.build_absolute_uri(
                reverse('verify_email', args=[str(ev.token)])
            )

            # Uncomment when ready to send email and user will verify it 
            # send_mail(
            #     subject="Please verify your email",
            #     message=f"Hi {user.first_name},\n\nThanks for registering! Verify your email:\n{verify_url}",
            #     from_email=settings.EMAIL_HOST_USER,
            #     recipient_list=[user.email],
            # )

            return render(request, 'renter/verify_sent.html')

        except Exception as e:
            print("Registration error:", e)
            return redirect('/register?error=internal')

    else:
        print("Form not submitted")
        return redirect('/register')



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
            

            # Need tp add Minimum Standard Report 

            return render(request, 'renter/welcome.html', {
                'renter': renter,
                'room_conditions': room_conditions,
                'properties' : properties,
                'appliance_reports': appliance_reports, 
                # include appliance reports here,
                'jobs': job_list,  # pass to template
                'minimum_reports': minimum_reports 
            })

        elif ThirdParty.objects.filter(user=user).exists():
            return redirect('thirdparty_account')

    except Exception as e:
        print("Welcome view error:", e)

    return render(request, 'renter/welcome.html', {
                'renter': renter,
                'room_conditions': room_conditions,
                'properties' : properties,
                'appliance_reports': appliance_reports, 
                'minimum_reports': minimum_reports,
                # 'jobs': job_list,  

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
    renter = Renter.objects.filter(user=user).first()

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        pin = request.POST.get('pin')  # For future validation maybe
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')

        # Split full name into first and last name
        if name:
            name_parts = name.strip().split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''

        user.email = email
        user.save()

        # Save Renter details
        if renter:
            renter.phone = phone
            renter.contact_person = name
            renter.email = email
            renter.date_of_birth = dob
            renter.gender = gender
            renter.save()

        messages.success(request, "Your account has been updated.")
        return redirect('renter_account')  # Adjust if you use a different URL name

    return render(request, 'renter/home/account.html', {
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



# Create Jobs here 

