from django.shortcuts import render, redirect,get_object_or_404
from datetime import datetime

from renter.models import Renter, Property, ConditionReport,EmailVerification, FailedLoginAttempt, MinimumStandardReport
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

from .forms import JobForm
from trader.models import Jobs
from trader.models import TraderRegistration
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

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from agent.models.propertyAgent import Property

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import PropertyForm
from .forms import MinimumStandardReportForm
from .forms import RenterRoomForm, RenterRoomAreaConditionForm
from renter.models import RenterRoom, RenterRoomAreaCondition
# 1. Index view for Properties
@login_required
def property_index(request):
    user = request.user
    try:
        renter = Renter.objects.get(user=user)
        properties = Property.objects.filter(renter=renter)
    except Renter.DoesNotExist:
        properties = []

    return render(request, 'renter/home/properties/renter_properties.html', {
        'properties': properties
    })


# def property_index(request):
#     properties = Property.objects.all()
#     return render(request, 'renter/renter/home/properties/renter_properties.html', {'properties': properties})


@login_required
def get_property(request, id):
    try:
        renter = Renter.objects.get(user=request.user)
        prop = Property.objects.get(id=id, renter=renter)
        data = {
            'id': prop.id,
            'name': prop.name,
            'city': prop.city,
            'status': prop.status,
        }
        return JsonResponse(data)
    except Property.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

@csrf_exempt
@login_required
def save_property(request):
    if request.method == 'POST':
        data = request.POST
        prop_id = data.get('id')
        name = data.get('name')
        city = data.get('city')
        status = data.get('status')

        try:
            renter = Renter.objects.get(user=request.user)
        except Renter.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'You are not a renter'})

        if prop_id:
            # UPDATE
            try:
                prop = Property.objects.get(id=prop_id, renter=renter)
                prop.name = name
                prop.city = city
                prop.status = status
                prop.save()
                return JsonResponse({'status': 'success'})
            except Property.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Property not found'})
        else:
            # CREATE
            try:
                agent = renter.agent_register if hasattr(renter, 'agent_register') else AgentRegister.objects.first()
                prop = Property.objects.create(
                    name=name,
                    city=city,
                    status=status,
                    agent=agent,
                    renter=renter
                )
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            user = request.user
            renter = Renter.objects.get(user=user)
            property.renter = renter

            # Optional: auto-assign agent
            if hasattr(renter, 'agent_register'):
                property.agent = renter.agent_register
            else:
                property.agent = AgentRegister.objects.first()

            property.save()
            messages.success(request, "Property added successfully.")
            return redirect('property_list')
    else:
        form = PropertyForm()

    return render(request, 'renter/home/properties/property_form.html', {'form': form})


@csrf_exempt
@login_required
def delete_property(request, id):
    if request.method == 'POST':
        try:
            renter = Renter.objects.get(user=request.user)
            prop = Property.objects.get(id=id, renter=renter)
            prop.delete()
            return JsonResponse({'status': 'success'})
        except Property.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Property not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



@method_decorator(login_required, name='dispatch')
class PropertyListView(ListView):
    model = Property
    template_name = 'renter/home/properties/property_list.html'
    context_object_name = 'properties'

    def get_queryset(self):
        try:
            renter = Renter.objects.get(user=self.request.user)
            return Property.objects.filter(renter=renter)
        except Renter.DoesNotExist:
            return Property.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agents'] = AgentRegister.objects.all()
        return context

@method_decorator(login_required, name='dispatch')
class PropertyCreateView(CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'renter/home/properties/property_form.html'
    success_url = reverse_lazy('property_list')

    def form_valid(self, form):
        agent = AgentRegister.objects.get(user=self.request.user)
        form.instance.agent = agent
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class PropertyUpdateView(UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'renter/home/properties/property_form.html'
    success_url = reverse_lazy('property_list')


@method_decorator(login_required, name='dispatch')
class PropertyDeleteView(DeleteView):
    model = Property
    template_name = 'renter/home/properties/property_confirm_delete.html'
    success_url = reverse_lazy('property_list')





@login_required
@csrf_exempt
def add_property(request):
    if request.method == 'POST':
        user = request.user
        try:
            renter = Renter.objects.get(user=user)
            agent_id = request.POST.get('agent_id')  #
            agent = AgentRegister.objects.get(id=agent_id)

            data = request.POST
            property_photo = request.FILES.get('property_photo')
            condition_report = request.FILES.get('condition_report')

            prop = Property.objects.create(
                renter=renter,
                agent=agent,  # ✅ssign agent
                name=data.get('name'),
                floor_count=data.get('floor_count'),
                city=data.get('city'),
                state=data.get('state'),
                address=data.get('address'),
                renter_name=data.get('renter_name'),
                renter_contact=data.get('renter_contact'),
                rent=data.get('rent'),
                postal_code=data.get('postal_code'),
                lease_start=data.get('lease_start'),
                lease_end=data.get('lease_end'),
                status=data.get('status'),
                property_photo=property_photo,
                condition_report=condition_report,
            )

            # return JsonResponse({
            #     'success': True,
            #     'message': 'Property added successfully.',
            #     'property_id': prop.id,
            #     'property_name': prop.name
            # })

            return redirect('/welcome/')

        except Exception as e:
            print("Error adding property:", e)
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)



    return JsonResponse({
        'success': False,
        'message': 'Only POST method allowed.'
    }, status=405)


@login_required
def delete_property(request, id):
    user = request.user
    try:
        renter = Renter.objects.get(user=user)
        prop = get_object_or_404(Property, id=id, renter=renter)
        prop.delete()
    except Exception as e:
        print("Error deleting property:", e)
    return redirect('/welcome/')



@login_required
def unlink_property(request, id):
    user = request.user
    try:
        renter = Renter.objects.get(user=user)
        prop = get_object_or_404(Property, id=id, renter=renter)
        prop.renter = None  #  unlink
        prop.save()
        return redirect('renter_welcome')
    except Exception as e:
        print("Unlink error:", e)
        return redirect



@login_required
def edit_property(request, id):
    if request.method == 'POST':
        try:
            prop = get_object_or_404(Property, id=id, renter__user=request.user)

            data = request.POST
            property_photo = request.FILES.get('property_photo')
            condition_report = request.FILES.get('condition_report')

            # Handle date fields safely
            lease_start = data.get('lease_start') or None
            lease_end = data.get('lease_end') or None
            lease_start = datetime.strptime(lease_start, "%Y-%m-%d").date() if lease_start else None
            lease_end = datetime.strptime(lease_end, "%Y-%m-%d").date() if lease_end else None

            # Update fields
            prop.name = data.get('name')
            prop.floor_count = data.get('floor_count')
            prop.city = data.get('city')
            prop.state = data.get('state')
            prop.address = data.get('address')
            prop.renter_name = data.get('renter_name')
            prop.renter_contact = data.get('renter_contact')
            prop.rent = data.get('rent')
            prop.postal_code = data.get('postal_code')
            prop.lease_start = lease_start
            prop.lease_end = lease_end
            prop.status = data.get('status')
            agent_id = data.get('agent_id')
            if agent_id:
                prop.agent_id = agent_id

            if property_photo:
                prop.property_photo = property_photo
            if condition_report:
                prop.condition_report = condition_report

            prop.save()
            return redirect('/properties/')
            # return JsonResponse({"success": True, "message": "Property updated successfully"})

        except Exception as e:
            print("Error updating property:", e)
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})



@login_required
def list_jobs(request):
    user = request.user
    try:
        renter = Renter.objects.get(user=user)
        jobs = Jobs.objects.filter(renter=renter)
    except Renter.DoesNotExist:
        jobs = []

    agents = AgentRegister.objects.all()
    traders = TraderRegistration.objects.all()
    return render(request, 'renter/home/jobs/renter_job_list.html', {
        'jobs': jobs,
        'agents': agents,
        'traders': traders,
    })


@csrf_exempt
@login_required
def add_job(request):
    if request.method == 'POST':
        try:
            renter = Renter.objects.get(user=request.user)

            agent = AgentRegister.objects.get(id=request.POST.get('agent_id'))
            trader = TraderRegistration.objects.get(id=request.POST.get('trader_id'))

            job = Jobs.objects.create(
                agent=agent,
                trader=trader,
                renter=renter,
                notes=request.POST.get('notes'),
                priority=request.POST.get('priority') == 'true',
                status=request.POST.get('status')
            )
            return redirect('/welcome/')
        except Exception as e:
            print("Add job error:", e)
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
def edit_job(request, id):
    if request.method == 'POST':
        try:
            job = get_object_or_404(Jobs, id=id, renter__user=request.user)

            job.agent_id = request.POST.get('agent_id')
            job.trader_id = request.POST.get('trader_id')
            job.notes = request.POST.get('notes')
            job.status = request.POST.get('status')
            job.priority = request.POST.get('priority') == 'true'
            job.save()

            return redirect('/properties/')  # Or redirect to job list
        except Exception as e:
            print("Edit job error:", e)
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)


@login_required
def delete_job(request, id):
    try:
        job = get_object_or_404(Jobs, id=id, renter__user=request.user)
        job.delete()
        return redirect('/welcome/')
    except Exception as e:
        print("Delete job error:", e)
        return redirect('/welcome/')




@login_required
def standard_report_list(request):
    reports = MinimumStandardReport.objects.filter(renter=request.user.renter)
    form = MinimumStandardReportForm()

    context = {
        'reports': reports,
        'form': form,
    }
    return render(request, 'renter/home/minimum_standard_reports/list.html', context)

@login_required
def add_standard_report(request):
    if request.method == 'POST':
        form = MinimumStandardReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.renter = request.user.renter
            report.save()
    return redirect('standard_report_list')

@login_required
def edit_standard_report(request, pk):
    report = get_object_or_404(MinimumStandardReport, pk=pk)
    if request.method == 'POST':
        form = MinimumStandardReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
    return redirect('standard_report_list')

@login_required
def delete_standard_report(request, pk):
    report = get_object_or_404(MinimumStandardReport, pk=pk)
    report.delete()
    return redirect('standard_report_list')



# Condition Reports
# List View (Main page with all data and modals)
def renter_room_list(request):
    rooms = RenterRoom.objects.filter(renter=request.user.renter).prefetch_related('conditions')
    return render(request, 'renter/home/condition_reports/renter_room_list.html', {'rooms': rooms})

# Create Room
def add_renter_room(request):
    if request.method == 'POST':
        form = RenterRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.renter = request.user.renter
            room.save()
    return redirect('renter_room_list')

# Edit Room
def edit_renter_room(request, pk):
    room = get_object_or_404(RenterRoom, pk=pk, renter=request.user.renter)
    if request.method == 'POST':
        form = RenterRoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
    return redirect('renter_room_list')

# Delete Room
def delete_renter_room(request, pk):
    room = get_object_or_404(RenterRoom, pk=pk, renter=request.user.renter)
    if request.method == 'POST':
        room.delete()
    return redirect('renter_room_list')

# Add AreaCondition
def add_area_condition(request, room_id):
    room = get_object_or_404(RenterRoom, pk=room_id, renter=request.user.renter)
    if request.method == 'POST':
        form = RenterRoomAreaConditionForm(request.POST)
        if form.is_valid():
            condition = form.save(commit=False)
            condition.room = room
            condition.save()
    return redirect('renter_room_list')

# Edit AreaCondition
def edit_area_condition(request, pk):
    condition = get_object_or_404(RenterRoomAreaCondition, pk=pk, room__renter=request.user.renter)
    if request.method == 'POST':
        form = RenterRoomAreaConditionForm(request.POST, instance=condition)
        if form.is_valid():
            form.save()
    return redirect('renter_room_list')

# Delete AreaCondition
def delete_area_condition(request, pk):
    condition = get_object_or_404(RenterRoomAreaCondition, pk=pk, room__renter=request.user.renter)
    if request.method == 'POST':
        condition.delete()
    return redirect('renter_room_list')



