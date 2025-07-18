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
from .models import AgentRegister, Property
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
        context['properties'] = Property.objects.all()
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

@method_decorator(login_required, name='dispatch')
class PropertyDetailView(DetailView):
    model = Property
    template_name = 'components/home/property_detail.html'
    context_object_name = 'property'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_form'] = AgentCreateRoomForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AgentCreateRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.property = self.object
            room.save()

            messages.success(request, f"Room created successfully!")
        else:
            messages.error(request, f"{form.errors}")

        return self.get(request, *args, **kwargs)

# ################## Manage Renters ##################
@method_decorator(login_required, name='dispatch')
class RenterListView(ListView):
    model = Renter
    template_name = 'components/home/manageRenters.html'  # you’ll create this
    context_object_name = 'renters'

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

# ################## Create Job Order ##################
@method_decorator(login_required, name='dispatch')
class AgentJobCreateView(CreateView):
    model = Jobs
    form_class = AgentCreateJobForm
    template_name = 'components/home/agent_job_form.html'
    success_url = reverse_lazy('agent_job_create')

    def form_valid(self, form):
        agent = AgentRegister.objects.filter(user=self.request.user).first()
        
        if not agent:
            form.add_error(None, "You must be an agent to create a job.")
            return self.form_invalid(form)
            
        job = form.save(commit=False)
        job.agent = agent

        try:
            job.save()

            # Send job creation email to agent
            send_mail(
                subject="Job Created Successfully",
                message=(
                    f"Hi {agent.name},\n\n"
                    f"Your job has been created successfully!\n"
                    f"Job Code: {job.job_code}\n\n"
                    f"Thank you for using FixMyHome."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[agent.email],
                fail_silently=False,
            )

            messages.success(self.request, f'Job created successfuly! Reference: {job.job_code}')
            return redirect(self.success_url)

        except Exception as e:
            form.add_error(None, f"Error saving job: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("Form is invalid:", form.errors)
        context = self.get_context_data(form=form)
        context['error'] = "There was an error updating your profile."
        return self.render_to_response(context)

@method_decorator(login_required, name='dispatch')
class JobListView(ListView):
    model = Jobs
    template_name = 'components/home/jobListAgent.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        # Return all jobs, ordered by priority and quoted_at
        queryset = super().get_queryset()
        return queryset.order_by('-priority', '-quoted_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['status_options'] = dict(Jobs._meta.get_field('status').choices)
        
        return context

@method_decorator(login_required, name='dispatch')
class AgentBidListView(ListView):
    model = Bidding
    template_name = 'components/home/agent_bid_list.html'
    context_object_name = 'bids'

    def get_queryset(self):
        return Bidding.objects.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_options'] = {
            None: 'Pending',
            True: 'Approved',
            False: 'Rejected',
        }
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
        return Jobs.objects.all().order_by('-priority', '-scheduled_at', '-approved_at', '-confirmed_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_options'] = dict(Jobs._meta.get_field('status').choices)
        return context