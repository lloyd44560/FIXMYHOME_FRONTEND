from django.shortcuts import render, redirect
from .models import Renter, FailedLoginAttempt
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

    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')
        next_url = request.POST.get('next') or '/welcome/'

        try:
            user_obj = User.objects.get(email=email)
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
                # unlock if time passed
                fail_record.is_locked = False
                fail_record.attempts = 0
                fail_record.locked_until = None
                fail_record.save()

            # 🔐 Check password
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                login(request, user)
                fail_record.attempts = 0
                fail_record.save()
                request.session.pop('locked_until', None)
                return redirect(next_url)
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
                    'error': f"Incorrect password. {remaining} attempt(s) left."
                })

        except User.DoesNotExist:
            return render(request, 'renter/login.html', {
                'error': 'User with this email does not exist.'
            })

    next_url = request.GET.get('next', '/welcome/')
    return render(request, 'renter/login.html', {'next': next_url})
    
@csrf_exempt
def register_renter(request):
    if request.method == 'POST':
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
        zip_code = request.POST.get('zip')
        address_line1 = request.POST.get('companyAddressLine1')
        address_line2 = request.POST.get('companyAddressLine2')
        postal_code = request.POST.get('companyPostalCode')
        upload_option = request.POST.get('uploadOption')
        property_image = request.FILES.get('propertyImage')

        # Optional: Save file
        if property_image:
            fs = FileSystemStorage()
            filename = fs.save(property_image.name, property_image)
            uploaded_file_url = fs.url(filename)
        else:
            uploaded_file_url = None

        #  1. Create the User
        if password == confirm_password:
            user = User.objects.create(
                username=email,  # or any unique username
                email=email,
                password=make_password(password),  # important: hash password
                first_name=name
            )
        else:
            return redirect('/register?error=password-mismatch')

        #  2. Create the linked Renter
        renter = Renter.objects.create(
            # user=user,  #  Link to auth_user
            phone=phone,
            name=name, 
            email=email,
            company_name=company,
            contact_person=contact_person,
            contact_phone=contact_phone,
            state=state,
            city=city,
            zip_code=zip_code,
            address_line1=address_line1,
            address_line2=address_line2,
            upload_option=upload_option,
            property_image=uploaded_file_url
        )

        return redirect('/login_renter/')
    else:
        print("Register Form is not submitted")
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

@login_required
def welcome(request):
    try:
        renter = Renter.objects.get(user=request.user)
    except Renter.DoesNotExist:
        renter = None  # Or redirect to profile setup page

    return render(request, 'renter/welcome.html', {'renter': renter})


def renter_create(request):
    if request.method == 'POST':
        form = RenterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = RenterForm()
    return render(request, 'renter_form.html', {'form': form})