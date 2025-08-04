import uuid
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from django.utils.timezone import now
from django.conf import settings
from django.urls import reverse_lazy
from django.core.mail import send_mail

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic.edit import UpdateView, FormView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone

from renter.models import Renter
from trader.models import Jobs, Bidding
from trader.models.servicesTrader import Services
from .models import AgentRegister, Property, Rooms
from .forms import CreateAgentFormClass, AgentEditProfileForm
from .forms import InvitationForm, AgentCreatePropertyForm, AgentCreateRoomForm
from .forms import RenterUpdateForm, AgentCreateJobForm, BiddingApprovalForm

# Create your views here.
class AgentRegistrationCreateView(CreateView):
    model = AgentRegister
    form_class = CreateAgentFormClass
    template_name = 'pages/registerAgent.html'
    success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            # Duplicate username or email check
            username = form.cleaned_data['name']
            email = form.cleaned_data['email']

            if User.objects.filter(username=username).exists():
                form.add_error('name', 'Username already exists.')
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Email already exists.')

            if form.errors:
                # Return with form errors due to duplicates
                return render(request, self.template_name, {'form': form})

            agent = form.save(commit=False)
            user = User.objects.create_user(
                username=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                is_superuser=1
            )
            agent.user = user
            agent.password = None
            agent.save()

            # Send agent registration success email
            send_mail(
                subject="Agent Registration Successful",
                message=(
                    f"Hi {agent.name},\n\n"
                    f"Your agent account has been created successfully!\n"
                    f"You can now log in and start using FixMyHome.\n\n"
                    f"Thank you for registering with us."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[agent.email],
                fail_silently=False,
            )

            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {'form': form})

# View for the home page
@method_decorator(login_required, name='dispatch')
class AgentHomeView(TemplateView):
    template_name = 'pages/homeAgent.html'
    success_url = reverse_lazy("home_agent")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get only active properties
        properties_list = Property.objects.filter(is_active__in=[True])

        # Set up pagination
        paginator = Paginator(properties_list, 10)  # Show 10 properties per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['properties'] = page_obj
        context['page_obj'] = page_obj  # For pagination controls

        agent = AgentRegister.objects.get(user=self.request.user)

        # Count by status & priority
        context['to_quote_urgent'] = Jobs.objects.filter(agent=agent, status='quoted', priority=True).count()
        context['to_quote_non_urgent'] = Jobs.objects.filter(agent=agent, status='quoted', priority=False).count()

        context['pending_urgent'] = Jobs.objects.filter(agent=agent, status='confirmed', priority=True).count()
        context['pending_non_urgent'] = Jobs.objects.filter(agent=agent, status='confirmed', priority=False).count()

        context['approved_urgent'] = Jobs.objects.filter(agent=agent, status='approved', priority=True).count()
        context['approved_non_urgent'] = Jobs.objects.filter(agent=agent, status='approved', priority=False).count()

        # Jobs Today (scheduled today)
        today = now().date()
        context['today_urgent'] = Jobs.objects.filter(agent=agent, scheduled_at__date=today, priority=True).count()
        context['today_non_urgent'] = Jobs.objects.filter(agent=agent, scheduled_at__date=today, priority=False).count()

        return context

@method_decorator(login_required, name='dispatch')
class AgentEditProfileView(UpdateView):
    model = AgentRegister
    form_class = AgentEditProfileForm
    template_name = "components/home/navigatorPages/viewProfileAgent.html"
    success_url = reverse_lazy('profile_agent')

    def get_object(self, queryset=None):
        try:
            fetchByRelatedField = self.model.objects.filter(user=self.request.user).first()
            fetchByName = self.model.objects.filter(name=str(self.request.user)).first()
            return fetchByRelatedField or fetchByName

        except self.model.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        agent = self.get_object()

        if agent:
            context['full_name'] = user.get_full_name() or agent.name
            context['email'] = agent.email
            context['phone'] = agent.phone
            context['address'] = agent.address_line_1
            context['addressTwo'] = agent.address_line_2

        else:
            context['error'] = "Agent profile not found."

        return context

    def form_valid(self, form):
        objectUpdate = self.get_object()

        # Fields to update
        fields = [
            'name', 'email', 'phone', 'agency_id', 'website', 'company_name',
            'company_address', 'company_email', 'company_landline',
            'contractor_license', 'service', 'state', 'municipality', 'city',
            'postal_code', 'address_line_1', 'address_line_2'
        ]

        for field in fields:
            setattr(objectUpdate, field, form.cleaned_data[field])

        objectUpdate.save(update_fields=fields)
        return redirect(self.success_url)

    def form_invalid(self, form):
        print("Form is invalid:", form.errors)
        context = self.get_context_data(form=form)
        context['error'] = "There was an error updating your profile."
        return self.render_to_response(context)

@method_decorator(login_required, name='dispatch')
class AgentEditSecurityView(FormView):
    template_name = "components/home/navigatorPages/editSecurityAgent.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profile_agent')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # PasswordChangeForm needs user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)  # Keeps session
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class PropertyCreateView(CreateView):
    template_name = "components/home/property_form.html"
    model = Property
    form_class = AgentCreatePropertyForm
    success_url = reverse_lazy("home_agent")

    def form_valid(self, form):
        userAgent = AgentRegister.objects.get(user=self.request.user)
        property = form.save(commit=False)
        property.agent = userAgent
        # Set the renter FK from the validated renter_name field
        if hasattr(form, 'cleaned_data') and 'renter_name' in form.cleaned_data:
            from renter.models import Renter
            renter_name = form.cleaned_data['renter_name']
            renter_qs = Renter.objects.filter(name__iexact=renter_name)
            if renter_qs.exists():
                property.renter = renter_qs.first()
        property.save()
        messages.success(self.request, "Property created successfully!")
        return redirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class PropertyUpdateView(UpdateView):
    model = Property
    form_class = AgentCreatePropertyForm
    template_name = 'components/home/property_form.html'
    success_url = reverse_lazy('manage_properties')

    def get_initial(self):
        initial = super().get_initial()
        property = self.get_object()
        if hasattr(property, 'renter') and property.renter:
            initial['renter_name'] = property.renter.name
        else:
            initial['renter_name'] = ""
        return initial

    def form_valid(self, form):
        property = form.save(commit=False)
        # Set the renter FK from the validated renter_name field
        if hasattr(form, 'cleaned_data') and 'renter_name' in form.cleaned_data:
            from renter.models import Renter
            renter_name = form.cleaned_data['renter_name']
            renter_qs = Renter.objects.filter(name__iexact=renter_name)
            if renter_qs.exists():
                property.renter = renter_qs.first()
        property.save()
        messages.success(self.request, 'Property details updated successfully.')
        return redirect(self.success_url)

@require_POST
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.delete()
    messages.success(request, f"Property '{property.name}' deleted.")
    return redirect('home_agent')

@require_POST
def archive_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.is_active = False
    property.save()
    messages.success(request, f"Property '{property.name}' has been archived.")
    return redirect('home_agent')

@method_decorator(login_required, name='dispatch')
class PropertyDetailView(DetailView):
    model = Property
    template_name = 'components/home/property_detail.html'
    context_object_name = 'property'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_form'] = AgentCreateRoomForm()
        context['job_form'] = AgentCreateJobForm()
        context['jobs'] = Jobs.objects.filter(property=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class RoomCreateView(CreateView):
    model = Rooms
    form_class = AgentCreateRoomForm
    template_name = 'components/home/property_detail.html'

    def form_valid(self, form):
        property_instance = get_object_or_404(Property, pk=self.kwargs['property_id'])
        form.instance.property = property_instance
        form.instance.renter = property_instance.renter or None  # Set renter from property
        messages.success(self.request, "Room created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create room. Please check the form.")
        return reverse_lazy('property_view', pk=self.kwargs['property_id'])

    def get_success_url(self):
        return reverse_lazy('property_view', kwargs={'pk': self.kwargs['property_id']})

# ################## Manage Renters ##################
@method_decorator(login_required, name='dispatch')
class RenterListView(ListView):
    model = Renter
    template_name = 'components/home/manageRenters.html'  # you’ll create this
    context_object_name = 'renters'

    def get_queryset(self):
        # Show all jobs, ordered by priority and scheduled/approved/confirmed date
        queryset = super().get_queryset()

        # Get filter parameters from request
        renter_name = self.request.GET.get('renter_name')

        # Apply filters if provided
        if renter_name:
            queryset = queryset.filter(name__icontains=renter_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Preserve filter values in template for form repopulation
        context['filter_renter'] = self.request.GET.get('renter_name', '')

        return context

class RenterUpdateView(UpdateView):
    model = Renter
    form_class = RenterUpdateForm
    template_name = 'components/home/editRenters.html'
    success_url = reverse_lazy('manage_renters')

    def get_object(self, queryset=None):
        # Get the renter object by pk from the URL
        pk = self.kwargs.get('pk')
        return get_object_or_404(Renter, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['renter'] = self.get_object()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Renter updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the renter.')
        return self.render_to_response(self.get_context_data(form=form))

@method_decorator(login_required, name='dispatch')
class AgentJobCreateView(CreateView):
    model = Jobs
    form_class = AgentCreateJobForm
    template_name = 'components/home/property_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_instance = get_object_or_404(Property, pk=self.kwargs['property_id'])
        context['property'] = property_instance
        context['room_form'] = AgentCreateRoomForm()
        context['job_form'] = self.get_form()
        context['jobs'] = Jobs.objects.filter(property=property_instance)
        return context

    def form_valid(self, form):
        agent = AgentRegister.objects.filter(user=self.request.user).first()

        if not agent:
            messages.error(self.request, "You must be an agent to create a job.")
            return self.form_invalid(form)

        try:
            property_instance = get_object_or_404(Property, pk=self.kwargs['property_id'])
            form.instance.property = property_instance
            form.instance.renter = property_instance.renter or None
            form.instance.agent = agent
            form.instance.property_photo = form.cleaned_data['property_photo'] if 'property_photo' in form.cleaned_data else None

            # Save the form first to get job_code
            response = super().form_valid(form)

            # Send job creation email to agent
            send_mail(
                subject="Job Created Successfully",
                message=(
                    f"Hi {agent.name},\n\n"
                    f"Your job has been created successfully!\n"
                    f"Job Code: {form.instance.job_code}\n\n"
                    f"Thank you for using FixMyHome."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[agent.email],
                fail_silently=False,
            )

            messages.success(self.request, f'Job created successfully! Reference: {form.instance.job_code}')
            return response

        except Exception as e:
            messages.error(self.request, f"Error saving job: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error creating the job. Please check the form.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        # Ensure reverse_lazy is converted to string
        return str(reverse_lazy('property_view', kwargs={'pk': self.kwargs['property_id']}))

@method_decorator(login_required, name='dispatch')
class AgentBidListView(ListView):
    model = Bidding
    template_name = 'components/home/agent_bid_list.html'
    context_object_name = 'bids'

    def get_queryset(self):
        # Show all jobs, ordered by priority and scheduled/approved/confirmed date
        queryset = super().get_queryset()

        # Filter only active properties
        queryset = queryset.filter(is_active=True)

        # Get filter parameters from request
        trader = self.request.GET.get('trader')
        is_approved = self.request.GET.get('status')
        approved_at = self.request.GET.get('approved_at')

        # Apply filters if provided
        if trader:
            queryset = queryset.filter(trader__name__icontains=trader)
        if approved_at:
            queryset = queryset.filter(approved_at=approved_at)

        if is_approved == 'true':
            queryset = queryset.filter(is_approved=True)
        elif is_approved == 'false':
            queryset = queryset.filter(is_approved=False)
        elif is_approved == '':
            queryset = queryset.filter(is_approved__isnull=True)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_options'] = {
            '': 'Pending',
            'true': 'Approved',
            'false': 'Rejected',
        }

        # Preserve filter values in template for form repopulation
        context['filter_trader'] = self.request.GET.get('trader', '')
        context['filter_is_approved'] = self.request.GET.get('status', '')
        context['filter_approved_at'] = self.request.GET.get('approved_at', '')

        return context

@method_decorator(login_required, name='dispatch')
class BiddingApprovalView(UserPassesTestMixin, UpdateView):
    model = Bidding
    form_class = BiddingApprovalForm
    template_name = 'pages/bidding_approval.html'
    success_url = reverse_lazy('agent_bid_list')

    def test_func(self):
        # Only allow agents to approve
        return hasattr(self.request.user, 'agentregister')

    def form_valid(self, form):
        bidding = form.save(commit=False)
        bidding.approved_at = timezone.now()
        bidding.approved_by = AgentRegister.objects.filter(user=self.request.user).first()
        bidding.save()
        messages.success(self.request, 'Bid approval status updated.')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class PropertiesListView(ListView):
    model = Property
    template_name = 'components/home/propertiesList.html'
    context_object_name = 'properties'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter only active properties
        queryset = queryset.filter(is_active=True)

        # Get filter parameters from request
        status = self.request.GET.get('status')
        address = self.request.GET.get('address')
        renter = self.request.GET.get('renter')

        # Apply filters if provided
        if status:
            queryset = queryset.filter(status=status)  # Fixed: assumed 'status' instead of 'state'
        if address:
            queryset = queryset.filter(address__icontains=address)  # Case-insensitive partial match
        if renter:
            queryset = queryset.filter(renter__name__icontains=renter)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Preserve filter values in template for form repopulation
        context['filter_status'] = self.request.GET.get('status', '')
        context['filter_address'] = self.request.GET.get('address', '')
        context['filter_renter'] = self.request.GET.get('renter', '')

        return context

@method_decorator(login_required, name='dispatch')
class InviteRenterView(FormView):
    template_name = 'components/home/invitationForm.html'
    form_class = InvitationForm
    success_url = reverse_lazy("renter_invitation")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        # Get extra POST data from modal
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        token = str(uuid.uuid4())

        invitation_link = self.request.build_absolute_uri(f"/register/?token={token}")
        send_mail(
            subject="You're invited to join!",
            message=f"Hi {name},\n\nYou've been invited! Register here: {invitation_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        messages.success(self.request, "Invitation sent successfully!")

        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class ActiveJobsListView(ListView):
    model = Jobs
    template_name = 'components/home/active_jobs_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        # Show all jobs, ordered by priority and scheduled/approved/confirmed date
        queryset = super().get_queryset()

        # Filter only active properties
        queryset = queryset.filter(is_active=True)

        # Get filter parameters from request
        status = self.request.GET.get('status')
        category = self.request.GET.get('category')
        priority = self.request.GET.get('priority')
        trader = self.request.GET.get('trader')
        scheduled_at = self.request.GET.get('scheduled_at')

        # Apply filters if provided
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category=category)
        if trader:
            queryset = queryset.filter(trader__name__icontains=trader)
        if scheduled_at:
            queryset = queryset.filter(scheduled_at=scheduled_at)
        if priority == 'true':
            queryset = queryset.filter(priority=True)
        elif priority == 'false':
            queryset = queryset.filter(priority=False)

        return queryset.order_by('-priority', '-scheduled_at', '-approved_at', '-confirmed_at')

    def get_context_data(self, **kwargs):
        category = self.request.GET.get('category')

        context = super().get_context_data(**kwargs)
        context['status_options'] = dict(Jobs._meta.get_field('status').choices)
        context['category_options'] = {
            service.id: service.description
            for service in Services.objects.all()
        }

        # Preserve filter values in template for form repopulation
        context['filter_status'] = self.request.GET.get('status', '')
        context['filter_category'] = int(category) if category and category.isdigit() else ''
        context['filter_priority'] = self.request.GET.get('priority', '')
        context['filter_trader'] = self.request.GET.get('trader', '')
        context['filter_scheduled_at'] = self.request.GET.get('scheduled_at', '')

        return context