from django.shortcuts import render, redirect
from .models import Renter
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from .forms import RenterForm

def home(request):
    return render(request, 'renter/home.html')

def register(request):

    if request.method == 'POST':
        data = request.POST
        files = request.FILES

        if Renter.objects.filter(email=data.get('email')).exists():
            return render(request, 'renter/register.html', {'error': 'Email already registered.'})

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

def login(request):
    return render(request, 'renter/login.html')

# def register_renter(request):
#     if request.method == 'POST':

#         data = request.POST
#         files = request.FILES

#         if Renter.objects.filter(email=data.get('email')).exists():
#             return render(request, 'renter/register.html', {'error': 'Email already registered.'})

#         renter = Renter.objects.create(
#             name=data.get('name'),
#             email=data.get('email'),
#             phone=data.get('phone'),
#             password=make_password(data.get('password')),

#             company_name=data.get('company'),
#             contact_person=data.get('contactPerson'),
#             contact_person_email=data.get('contactPersonEmail'),
#             contact_phone=data.get('contactPhone'),
#             state=data.get('state'),
#             city=data.get('city'),
#             zip_code=data.get('zip'),
#             company_address_line1=data.get('companyAddressLine1'),
#             company_address_line2=data.get('companyAddressLine2'),
#             company_postal_code=data.get('companyPostalCode'),
#             upload_option=data.get('uploadOption'),
#             property_image=files.get('propertyImage'),
#             floor_count=data.get('floorCount') or None,
#             room_count=data.get('roomCount') or None,
#             address_line1=data.get('houseAddressLine1'),
#             address_line2=data.get('houseAddressLine2'),
#             house_state=data.get('houseState'),
#             house_city=data.get('houseCity'),
#             house_zip=data.get('houseZip'),
#         )

#         return redirect('success')
#         return JsonResponse({'message': 'Registered successfully'})
#         return render(request, 'renter/login.html')
#     else:
#         return JsonResponse({'error': 'Invalid method'}, status=400)

def register_renter(request):
    if request.method == 'POST':
        form = RenterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # replace with your success redirect
    else:
        form = RenterForm()
    return render(request, 'register.html', {'form': form})


def welcome(request):
    return render(request, 'renter/welcome.html')



def renter_create(request):
    if request.method == 'POST':
        form = RenterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = RenterForm()
    return render(request, 'renter_form.html', {'form': form})