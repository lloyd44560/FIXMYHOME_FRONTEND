# thirdparty/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import ThirdParty
from renter.models import Renter, Property, ConditionReport
from trader.models import TraderRegistration
from agent.models import AgentRegister
from django.contrib.auth.decorators import login_required

def thirdparty_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        company_name = request.POST['company_name']
        contact_person = request.POST['contact_person']
        contact_email = request.POST['contact_email']
        phone = request.POST['phone']

        user = User.objects.create_user(username=username, password=password)
        third_party = ThirdParty.objects.create(
            user=user,
            company_name=company_name,
            contact_person=contact_person,
            contact_email=contact_email,
            phone=phone
        )
        return redirect('thirdparty_login')

    return render(request, 'thirdparty/register.html')

def thirdparty_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('thirdparty_home')
        else:
            return render(request, 'thirdparty/login.html', {'error': 'Invalid credentials'})

    return render(request, 'thirdparty/login.html')

@login_required
def thirdparty_home(request):

    renters = Renter.objects.all()
    properties = Property.objects.all()
    traders = TraderRegistration.objects.all()
    agents = AgentRegister.objects.all()

    users_count = User.objects.count()
    properties_count = Property.objects.count()
    agents_count = AgentRegister.objects.count()
    traders_count = TraderRegistration.objects.count()
    reports_count = ConditionReport.objects.count()  # only if this exists

    context = {
        'renters': renters,
        'properties': properties,
        'traders': traders,
        'agents': agents,

        'users_count': users_count,
        'properties_count': properties_count,
        'agents_count': agents_count,
        'traders_count': traders_count,
        'reports_count': reports_count,  # optional

    }

    return render(request, 'thirdparty/welcome.html', context)

@login_required
def third_party_account(request):

    user = request.user


    thirdparty = ThirdParty.objects.filter(user=user).first()

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('contact_email', '')
        phone = request.POST.get('phone', '')
        gender = request.POST.get('gender', '')
        dob = request.POST.get('dob', '')

        # Update user fields
        if name:
            parts = name.split(' ')
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = ' '.join(parts[1:])
        if email:
            user.email = email
        user.save()

        # Update thirdparty fields
        if thirdparty:
            thirdparty.contact_email = email
            thirdparty.phone = phone
            thirdparty.gender = gender
            thirdparty.dob = dob
            thirdparty.save()

        return redirect('third_party_account')  # Redirect after POST

    return render(request, 'thirdparty/home/account.html', {
        'user': user,
        'thirdparty': thirdparty
    })
