from django.shortcuts import render, redirect,get_object_or_404
from datetime import datetime

from renter.models import Renter, Property, ConditionReport,EmailVerification, FailedLoginAttempt, MinimumStandardReport,RequestReport
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
from trader.models import Jobs, JobImage, Bidding
from trader.models.servicesTrader import Services
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
from .forms import RenterRoomForm, RenterRoomAreaConditionForm, RoomApplianceReportForm
from renter.models import RenterRoom, RenterRoomAreaCondition, RoomApplianceReport,MainConditionReport, ConditionReportRoom
from django.db import transaction
import re
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

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
    paginate_by = 5  # Number of items per page

    def get_queryset(self):
        try:
            renter = Renter.objects.get(user=self.request.user)
            queryset = Property.objects.filter(renter=renter)

            # Search filter
            query = self.request.GET.get('q')
            if query:
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(city__icontains=query) |
                    Q(state__icontains=query)
                )
            return queryset
        except Renter.DoesNotExist:
            return Property.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agents'] = AgentRegister.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
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
                agent=agent,  #  Assign agent
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

            return redirect('/properties/')

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
    return redirect('/properties/')



@login_required
def unlink_property(request, id):
    user = request.user
    try:
        renter = Renter.objects.get(user=user)
        prop = get_object_or_404(Property, id=id, renter=renter)
        prop.renter = None  #  unlink
        prop.save()
        return redirect('/properties/')
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

############################################################################################### Renter Maintenance Requests #########################################################################################################
@login_required
def list_jobs(request):
    user = request.user
    search_query = request.GET.get('q', '')

    try:
        renter = Renter.objects.get(user=user)
        jobs = Jobs.objects.filter(renter=renter)

        if search_query:
            jobs = jobs.filter(
                Q(job_code__icontains=search_query) |
                Q(status__icontains=search_query) |
                Q(notes__icontains=search_query) |
                Q(category__description__icontains=search_query)
            )

        # --- Attach all bidding records per job ---
        for job in jobs:
            job.bids = Bidding.objects.all()

    except Renter.DoesNotExist:
        jobs = Jobs.objects.none()

    # Pagination
    paginator = Paginator(jobs.order_by('-approved_at'), 5)
    page_number = request.GET.get('page')
    page_jobs = paginator.get_page(page_number)

    agents = AgentRegister.objects.all()
    traders = TraderRegistration.objects.all()
    services = Services.objects.filter(is_active=True)
    all_bids = Bidding.objects.all()

    return render(request, 'renter/home/jobs/renter_job_list.html', {
        'jobs': page_jobs,
        'agents': agents,
        'traders': traders,
        'services': services,
        'bids': all_bids,
        'search_query': search_query,
    })



@csrf_exempt
@login_required
def add_job(request):
    if request.method == 'POST':
        try:
            #  Get renter from current user
            renter = Renter.objects.get(user=request.user)

            # 2. Get the property tagged to this renter
            property_obj = Property.objects.filter(renter=renter).first()
            if not property_obj:
                messages.error(request, "No property found for this renter.")
                return redirect('/maintenance/')

            # 3. Get the agent automatically from that property
            agent = property_obj.agent  # assuming Property has ForeignKey to AgentRegister

            if not agent:
                messages.error(request, "No agent assigned to this property.")
                return redirect('/maintenance/')

            # 4. Get selected service (category)
            service_id = request.POST.get('category')
            service = Services.objects.get(id=service_id)

            # 5. Determine priority (based on service urgency)
            priority = service.isurgent

            # 6. Create the job
            job = Jobs.objects.create(
                agent=agent,             # from property
                renter=renter,
                property=property_obj,   # linked property
                notes=request.POST.get('notes'),
                category=service,
                priority=priority
            )

            #7. Handle image uploads
            images = request.FILES.getlist('images')
            for img in images:
                JobImage.objects.create(job=job, image=img)

            # 8. Success message
            messages.success(request, "Maintenance Request created successfully.")
            return redirect('/maintenance/')

        except Exception as e:
            print("Add job error:", e)
            messages.error(request, f"Error creating Maintenance Request: {e}")
            return redirect('/maintenance/')

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
# @csrf_exempt
# @login_required
# def edit_job(request, job_id):
#     if request.method == 'POST':
#         try:
#             job = get_object_or_404(Jobs, id=job_id, renter__user=request.user)

#             # Update foreign keys
#             agent_id = request.POST.get('agent_id')
#             category_id = request.POST.get('category')

#             job.agent = AgentRegister.objects.get(id=agent_id) if agent_id else job.agent
#             job.category = ServiceCategory.objects.get(id=category_id) if category_id else job.category
#             job.notes = request.POST.get('notes', '')

#             # Update priority based on category's is_urgent
#             if job.category.is_urgent:
#                 job.priority = True
#             else:
#                 job.priority = False

#             job.save()

#             return redirect('/maintenance/')  # or return JsonResponse if using AJAX
#         except Exception as e:
#             print("Edit job error:", e)
#             return JsonResponse({'success': False, 'message': str(e)}, status=500)

#     return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required
def edit_job(request, job_id):
    renter = get_object_or_404(Renter, user=request.user)  # or username/email if that's how linked
    job = get_object_or_404(Jobs, id=job_id, renter=renter)
    if request.method == "POST":
        try:
            # Update foreign keys
            agent_id = request.POST.get("agent_id")
            category_id = request.POST.get("category")

            if agent_id:
                job.agent = AgentRegister.objects.get(id=agent_id)
            if category_id:
                job.category = Services.objects.get(id=category_id)

            # Priority logic
            service = job.category
            job.priority = service.isurgent

            # Update simple fields
            job.notes = request.POST.get("notes", "")
            job.issue_found_at = request.POST.get("issue_found_at") or None
            job.renter_availability = request.POST.get("renter_availability") or None
            job.issue_been_fixed_before = "issue_been_fixed_before" in request.POST

            job.save()

            # Handle image deletions
            delete_ids = request.POST.getlist("delete_images")
            if delete_ids:
                JobImage.objects.filter(id__in=delete_ids, job=job).delete()

            # Handle new uploads
            images = request.FILES.getlist("images")
            for img in images:
                JobImage.objects.create(job=job, image=img)
            messages.success(request, "Maintenance Request updated successfully.")
            return redirect("/maintenance/")
        except Exception as e:
            print("Edit job error:", e)
            return JsonResponse({"success": False, "message": str(e)}, status=500)
            messages.error(request, f"Error updating Maintenance Request: {e}")
            return redirect("/maintenance/")

    return JsonResponse({"success": False, "message": "Invalid request"}, status=405)



@login_required
def delete_job(request, id):
    try:
        job = get_object_or_404(Jobs, id=id)
        job.delete()
        return redirect('/maintenance/')
    except Exception as e:
        print("Delete job error:", e)
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
        messages.error(request, f"Maintenance Request deleted: {e}")


##################################################################################################################### Renter Min. Standard Report ########################################################################################################
@login_required
def standard_report_list(request):
    renter = request.user.renter
    search_query = request.GET.get('q', '')

    reports = MinimumStandardReport.objects.filter(renter=renter)

    # Apply search
    if search_query:
        reports = reports.filter(
            Q(tenant_name__icontains=search_query) |
            Q(audit_no__icontains=search_query) |
            Q(auditor__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    # Paginate (5 per page)
    paginator = Paginator(reports.order_by('-id'),4)
    page_number = request.GET.get('page')
    page_reports = paginator.get_page(page_number)

    form = MinimumStandardReportForm()
    context = {
        'reports': page_reports,
        'form': form,
        'search_query': search_query,
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

def renter_room_list(request):
    renter = request.user.renter  # Get the current renter

    # Only get rooms for this renter
    rooms = RenterRoom.objects.filter(renter=renter).prefetch_related('conditions')

    # Only get properties for this renter
    properties = Property.objects.filter(renter=renter)

    # Pass renter explicitly in case needed in the form or template
    return render(request, 'renter/home/condition_reports/renter_room_list.html', {
        'rooms': rooms,
        'properties': properties,
        'renter': renter,  # useful if you pass renter to modals/forms
    })

def add_renter_room(request):
    if request.method == 'POST':
        form = RenterRoomForm(request.POST)
        if form.is_valid():
            renter_room = form.save(commit=False)
            renter_room.renter = request.user.renter  # assign renter here
            renter_room.save()
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


@csrf_exempt
def renter_room_list(request):
    renter = request.user.renter

    #  Only get properties owned by this renter
    properties = Property.objects.filter(renter=renter)

    #  Get property filter from GET param
    property_id = request.GET.get('property')

    #  Filter rooms accordingly
    rooms = RenterRoom.objects.filter(renter=renter).select_related('property').prefetch_related('area_conditions')

    if property_id:
        rooms = rooms.filter(property_id=property_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_room':
            form = RenterRoomForm(request.POST)
            form.fields['property'].queryset = properties
            if form.is_valid():
                room = form.save(commit=False)
                room.renter = renter
                room.save()
                return redirect('/renter-rooms/')
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

        elif action == 'edit_room':
            room = get_object_or_404(RenterRoom, id=request.POST.get('room_id'), renter=renter)
            form = RenterRoomForm(request.POST, instance=room)
            form.fields['property'].queryset = properties
            if form.is_valid():
                form.save()
                return redirect('/renter-rooms/')
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

        elif action == 'delete_room':
            room = get_object_or_404(RenterRoom, id=request.POST.get('room_id'), renter=renter)
            room.delete()
            return redirect('/renter-rooms/')

        elif action == 'add_area_condition':
            from .forms import RenterRoomAreaConditionForm
            form = RenterRoomAreaConditionForm(request.POST, request.FILES)
            room_id = request.POST.get('room_id')
            if form.is_valid():
                area_condition = form.save(commit=False)
                area_condition.room_id = room_id
                area_condition.save()
                return redirect('/renter-rooms/')
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return render(request, 'renter/home/condition_reports/renter_room_list.html', {
        'rooms': rooms,
        'properties': properties,
        'selected_property': property_id,
    })




###################################################################################################### All Condition Report Functions ####################################################################################################
@csrf_exempt
@login_required
def save_condition_report(request):
    if request.method == 'POST':
        renter = request.user.renter
        report_number = request.POST.get('report_number')
        uploaded_file = request.FILES.get('uploaded_file')
        # Create the main report
        report = MainConditionReport.objects.create(
            report_number=report_number,
            renter=renter,
            uploaded_file=uploaded_file
        )

        room_index = 0
        while True:
            room_name = request.POST.get(f'room_name_{room_index}')
            if not room_name:
                break  # Done with rooms

            room_desc = request.POST.get(f'room_description_{room_index}')
            # You can also assign a property here if needed

            # Create the room
            room = RenterRoom.objects.create(
                renter=renter,
                room_name=room_name,
                description=room_desc
            )

            # Link it to the report
            ConditionReportRoom.objects.create(
                report=report,
                room=room
            )

            # Handle conditions inside this room
            condition_index = 0
            while True:
                area = request.POST.get(f'area_name_{room_index}_{condition_index}')
                if not area:
                    break  # Done with conditions for this room
                status = request.POST.get(f'status_{room_index}_{condition_index}')
                remarks = request.POST.get(f'remarks_{room_index}_{condition_index}')
                photo = request.FILES.get(f'photo_{room_index}_{condition_index}')

                RenterRoomAreaCondition.objects.create(
                    room=room,
                    area_name=area,
                    status=status,
                    remarks=remarks,
                    photo=photo
                )
                condition_index += 1

            room_index += 1

        messages.success(request, "Condition Report created successfully.")
        return redirect('condition_report_list')
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_condition_report_data(request, report_id):
    report = get_object_or_404(MainConditionReport, pk=report_id)
    data = {
        "id": report.id,
        "report_number": report.report_number,
        "rooms": [],
    }

    for cr_room in report.report_rooms.all():
        room_data = {
            "id": cr_room.room.id,
            "room_name": cr_room.room.room_name,
            "conditions": [],
        }

        for condition in cr_room.room.area_conditions.all():
            room_data["conditions"].append({
                "area_name": condition.area_name,
                "status": condition.status,
                "remarks": condition.remarks,
                "photo": condition.photo.url if condition.photo else ""
            })

        data["rooms"].append(room_data)

    return JsonResponse(data)

@login_required
def condition_report_list(request):
    renter = get_object_or_404(Renter, user=request.user)
    room_filter = request.GET.get('room_name', '')

    reports = MainConditionReport.objects.filter(renter=renter).select_related(
        'renter__user'
    ).prefetch_related(
        'report_rooms__room__area_conditions'
    )

    #  Fix this filter
    if room_filter:
        reports = reports.filter(
            report_rooms__room__room_name__iexact=room_filter
        ).distinct()

    room_names = RenterRoom.objects.filter(renter=renter).values_list(
        'room_name', flat=True
    ).distinct().order_by('room_name')

    return render(request, 'renter/home/condition_reports/condition_report_list.html', {
        'reports': reports,
        'room_names': room_names,
    })

@login_required
@csrf_exempt
def edit_condition_report(request, report_id):
    report = get_object_or_404(MainConditionReport, id=report_id, renter=request.user.renter)

    if request.method == 'POST':
        print(request.POST)  # Add this line to see all POST data


        # new_rooms_json = request.POST.get("new_rooms_json")
        print("=== DEBUG new_rooms_json ===")
        # print(new_rooms_json)

        # Pwede ka rin mag return muna ng HttpResponse para makita agad
        # return HttpResponse(f"Received JSON: {new_rooms_json}")


        print("\n=== DEBUG: POST DATA ===")
        for k, v in request.POST.items():
            print(f"{k}: {v}")
        print("=== DEBUG: FILES ===")
        for k, f in request.FILES.items():
            print(f"{k}: {f}")
        print("========================\n")

        new_rooms_json = request.POST.get("new_rooms_json")
        if new_rooms_json:
            try:
                new_rooms = json.loads(new_rooms_json)
            except json.JSONDecodeError as e:
                # return HttpResponse(f"Invalid JSON data: {e}")
                print("Invalid JSON data:")
            with transaction.atomic():
                for room_data in new_rooms:
                    room_name = room_data.get("room_name", "").strip()
                    room_description = room_data.get("room_description", "").strip()

                    if not room_name:
                        continue  # Skip if no room name

                    # Gumawa ng bagong room record
                    new_room = RenterRoom.objects.create(
                        renter=request.user.renter,
                        room_name=room_name,
                        description=room_description
                    )

                    # I-link ang bagong room sa report
                    ConditionReportRoom.objects.create(
                        report=report,
                        room=new_room
                    )

                    # Gumawa ng area conditions para sa bawat area
                    areas = room_data.get("areas", [])
                    for area in areas:
                        area_name = area.get("area_name", "").strip()
                        status = area.get("status", "").strip() or "Clean"  # default "Clean"
                        remarks = area.get("remarks", "").strip()

                        if not area_name:
                            continue  # Skip if no area name

                        RenterRoomAreaCondition.objects.create(
                            room=new_room,
                            area_name=area_name,
                            status=status,
                            remarks=remarks
                        )

            # return HttpResponse("Rooms and areas saved successfully.")

        # return HttpResponse("No new_rooms_json data found.")

        try:
            with transaction.atomic():
                # Update existing rooms
                print("\n--- Updating existing rooms ---")
                for idx, room_link in enumerate(report.report_rooms.all(), start=1):
                    current_name = room_link.room.room_name
                    room_name_key = f"room_name_{room_link.room.id}"
                    new_name = request.POST.get(room_name_key)
                    print(f"room_name_key: {room_name_key}, POST value: {request.POST.get(room_name_key)}")
                    print(f"Room {idx} current name: {current_name}, new name: {new_name}")

                    if new_name and new_name.strip() != current_name:
                        room_link.room.room_name = new_name.strip()
                        room_link.room.save()
                        print(f"✔ Room {idx} name updated to: {new_name}")

                # Update existing conditions
                print("\n--- Updating existing conditions ---")
                rooms = [rr.room for rr in report.report_rooms.all()]
                for condition in RenterRoomAreaCondition.objects.filter(room__in=rooms):
                    print(f"Condition {condition.id} BEFORE: {condition.area_name} | {condition.status} | {condition.remarks}")
                    condition.area_name = request.POST.get(f'area_name_{condition.id}', condition.area_name)
                    condition.status = request.POST.get(f'status_{condition.id}', condition.status)
                    condition.remarks = request.POST.get(f'remarks_{condition.id}', condition.remarks)

                    uploaded_photo = request.FILES.get(f'photo_{condition.id}')
                    if uploaded_photo:
                        condition.photo = uploaded_photo
                        print(f"✔ Condition {condition.id} photo updated.")

                    condition.save()
                    print(f"✔ Condition {condition.id} updated to: {condition.area_name} | {condition.status} | {condition.remarks}")

                # Handle NEW rooms & conditions
                # Hanapin lahat ng keys na nagsisimula sa 'new_room_name'
                new_room_keys = [key for key in request.POST.keys() if key.startswith("new_room_name")]
                print(f" Found new room keys: {new_room_keys}")

                # Update uploaded file for the whole report
                uploaded_file = request.FILES.get('uploaded_file')
                if uploaded_file:
                    report.uploaded_file = uploaded_file
                    report.save()
                    print(f"✔ Uploaded file for report {report.id} updated.")

                # messages.success(request, "Condition Report created successfully.")
                # return redirect('condition_report_list')
                messages.success(request, "Condition Report updated successfully.")
                print("✔ All updates committed successfully.")
                return redirect('condition_report_list')

        except Exception as e:
            messages.error(request, f"Error updating report: {e}")
            print(f"Error: {e}")

    return redirect('condition_report_list')

@login_required
def delete_renter_room(request, pk):
    room = get_object_or_404(RenterRoom, pk=pk)
    if room.renter == request.user.renter:
        room.delete()
    return redirect('condition_report_list')

@login_required
def edit_renter_room(request, pk):
    room = get_object_or_404(RenterRoom, pk=pk, renter=request.user.renter)
    if request.method == 'POST':
        form = RenterRoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('condition_report_list')
    else:
        form = RenterRoomForm(instance=room)
    return render(request, 'renter/home/condition_reports/edit_room_modal.html', {
        'form': form,
        'room': room
    })




######################################################################################################X## Appliance Reports Functionalities ######################################################################################################
@login_required
def appliance_report_list(request):
    renter = request.user.renter
    reports = RoomApplianceReport.objects.filter(renter=renter)
    rooms = RenterRoom.objects.filter(renter=renter)

    # Filters
    room_id = request.GET.get('room')
    brand = request.GET.get('brand')
    model_serial = request.GET.get('model_serial')

    if room_id:
        reports = reports.filter(room_id=room_id)

    if brand:
        reports = reports.filter(brand__icontains=brand)

    if model_serial:
        reports = reports.filter(model_serial__icontains=model_serial)

    # Pagination
    paginator = Paginator(reports.order_by('-id'), 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'rooms': rooms,
        'reports': page_obj.object_list,
        'room_filter': room_id,
        'brand_filter': brand,
        'model_serial_filter': model_serial,
    }

    return render(request, 'renter/home/appliance_reports/appliance_report_list.html', context)


@login_required
def appliance_report_create(request):

    try:
        renter = request.user.renter
    except Exception:
        messages.error(request, "No renter profile found for the logged-in user.")
        return redirect('appliance_report_list')

    if request.method == 'POST':
        room_id = request.POST.get('room')
        window_height = request.POST.get('window_height')
        window_length = request.POST.get('window_length')
        window_width = request.POST.get('window_width')
        brand = request.POST.get('brand')
        model_serial = request.POST.get('model_serial')
        location = request.POST.get('location')
        comments = request.POST.get('comments')
        appliance_photo = request.FILES.get('appliance_photo')

        photo1 = request.FILES.get('photo1')
        photo2 = request.FILES.get('photo2')
        photo3 = request.FILES.get('photo3')
        photo4 = request.FILES.get('photo4')
        photo5 = request.FILES.get('photo5')


        room = RenterRoom.objects.get(id=room_id)

        RoomApplianceReport.objects.create(
            room=room,
            window_height=window_height,
            window_length=window_length,
            window_width=window_width,
            brand=brand,
            model_serial=model_serial,
            location=location,
            comments=comments,
            appliance_photo=appliance_photo,
            renter=renter,
            photo1=photo1,
            photo2=photo2,
            photo3=photo3,
            photo4=photo4,
            photo5=photo5,
        )

        return redirect('appliance_report_list')

    rooms = RenterRoom.objects.all()
    return render(request, 'appliance_report_create.html', {
        'rooms': rooms
    })


@login_required
@require_POST
def edit_appliance_report(request, report_id):
    renter = request.user.renter

    try:
        report = RoomApplianceReport.objects.get(id=report_id, renter=renter)
    except RoomApplianceReport.DoesNotExist:
        messages.error(request, "Appliance report not found.")
        return redirect('appliance_report_list')

    report.room_id = request.POST.get('room')
    report.window_height = request.POST.get('window_height')
    report.window_length = request.POST.get('window_length')
    report.window_width = request.POST.get('window_width')
    report.brand = request.POST.get('brand')
    report.model_serial = request.POST.get('model_serial')
    report.location = request.POST.get('location')
    report.comments = request.POST.get('comments')

    # Main appliance photo
    if 'appliance_photo' in request.FILES:
        report.appliance_photo = request.FILES['appliance_photo']

    # Additional photos (photo1–photo5)
    for i in range(1, 6):
        file_key = f'photo{i}'
        if file_key in request.FILES:
            setattr(report, file_key, request.FILES[file_key])

    report.save()
    messages.success(request, "Appliance report updated.")
    return redirect('appliance_report_list')

def delete_appliance_report(request, pk):
    report = get_object_or_404(RoomApplianceReport, pk=pk, renter=request.user.renter)
    report.delete()
    messages.success(request, 'Appliance Report deleted successfully.')
    return redirect('appliance_report_list')

# Experimental all in one report view

def notebook_view(request):
    return render(request, 'renter/home/notebook.html')




# Request of Renter to Agent for Reports



def request_report_list(request):
    reports = RequestReport.objects.all().order_by('-date_requested')
    report_type = request.GET.get('report_type')
    agent_id = request.GET.get('agent')

    if report_type:
        reports = reports.filter(report_type=report_type)
    if agent_id:
        reports = reports.filter(agent__id=agent_id)

    renters = Renter.objects.all()
    agents = AgentRegister.objects.all()
    return render(request, 'renter/home/reports/request_report_list.html', {
        'reports': reports,
        'renters': renters,
        'agents': agents,
    })

def add_request_report(request):
    try:
        renter = request.user.renter
    except Exception:
        messages.error(request, "No renter profile found for the logged-in user.")
        return redirect('request_report_list')

    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        reason = request.POST.get('reason')
        agent_id = request.POST.get('agent')

        agent = get_object_or_404(AgentRegister, id=agent_id)

        # Save the report
        report = RequestReport.objects.create(
            report_type=report_type,
            reason=reason,
            renter=renter,
            agent=agent,
            date_requested=timezone.now(),
        )

        # ------------------------
        #  Send email to agent
        # ------------------------
        subject = f"New Report Request from {renter.user.get_full_name() or renter.user.username}"

        message = (
            f"Dear {agent.name},\n\n"
            f"A renter has submitted a new request report assigned to you.\n\n"
            f" Report Type: {report.get_report_type_display()}\n"
            f" Reason: {report.reason}\n"
            f" Renter: {renter.user.get_full_name()} ({renter.user.email})\n"
            f" Date Requested: {report.date_requested.strftime('%B %d, %Y %I:%M %p')}\n\n"
            f"Please log in to the FixMyHome system to review the details and take the necessary action.\n\n"
            f"Thank you for your continued support in assisting renters.\n\n"
            f"Best regards,\n"
            f"The FixMyHome Team"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[agent.email],
                fail_silently=False,
            )
        except Exception as e:
            messages.warning(request, f"Report saved but email could not be sent. Error: {str(e)}")

        messages.success(request, "Request report created and notification sent to the agent.")
        return redirect('request_report_list')

    return redirect('request_report_list')


def edit_request_report(request, pk):
    report = get_object_or_404(RequestReport, pk=pk)

    if request.method == 'POST':
        report.report_type = request.POST.get('report_type')
        report.reason = request.POST.get('reason')

        # Force renter = logged-in user’s renter
        try:
            renter = Renter.objects.get(user=request.user)
            report.renter = renter
        except Renter.DoesNotExist:
            return HttpResponse("No renter profile found for this user.", status=400)

        # Update agent if provided
        agent_id = request.POST.get('agent')
        if agent_id:
            report.agent = get_object_or_404(AgentRegister, id=agent_id)

        report.save()
        return redirect('request_report_list')  # make sure this matches urls.py

    return redirect('request_report_list')


def delete_request_report(request, pk):
    report = get_object_or_404(RequestReport, pk=pk)
    if request.method == 'POST':
        report.delete()
        return redirect('request_report_list')


def calendar_view(request):
    return render(request, "renter/home/calendar/calendar.html")

@csrf_exempt
def add_event(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title")
        start = parse_date(data.get("start"))
        end = parse_date(data.get("end")) if data.get("end") else None

        event = Event.objects.create(title=title, start=start, end=end)
        return JsonResponse({
            "id": event.id,
            "title": event.title,
            "start": str(event.start),
            "end": str(event.end) if event.end else None
        })

def event_list(request):
    events = list(Event.objects.all().values("id", "title", "start", "end"))
    for e in events:
        e["start"] = e["start"].isoformat() if e["start"] else None
        e["end"] = e["end"].isoformat() if e["end"] else None
    return JsonResponse(events, safe=False, json_dumps_params={"cls": DjangoJSONEncoder})



@login_required
def renter_chat(request):
    chat_url = "/chat/all_jobs/"  # This points to the chat app
    return render(request, 'renter/home/renter_chat.html', {"chat_url": chat_url})
