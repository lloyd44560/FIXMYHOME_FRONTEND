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

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic.edit import UpdateView, FormView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.contrib import messages

from renter.models import Renter
from trader.models import Jobs
from .models import AgentRegister, Property
from .forms import CreateAgentFormClass, AgentEditProfileForm
from .forms import InvitationForm, AgentCreatePropertyForm, AgentCreateRoomForm
from .forms import RenterUpdateForm, AgentCreateJobForm

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
class AgentHomeView(FormView):
    template_name = 'pages/homeAgent.html'
    form_class = InvitationForm
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

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        token = str(uuid.uuid4())

        # Save the invitation
        # Invitation.objects.create(
        #     email=email,
        #     token=token,
        #     invited_by=self.request.user  # you must be logged in!
        # )

        invitation_link = self.request.build_absolute_uri(f"/register/")

        send_mail(
            subject="You're invited to join!",
            message=f"Hi {name},\n\nYou've been invited! Register here: {invitation_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        messages.success(self.request, "Invitation sent successfully!")
        return super().form_valid(form)

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
            'name', 'email', 'phone', 'agency_id', 'website', 'notes', 'password',
            'company_name', 'company_address', 'company_email', 'company_landline',
            'contractor_license', 'service', 'state', 'municipality', 'city',
            'postal_code', 'address_line_1', 'address_line_2'
        ]

        for field in fields:
            setattr(objectUpdate, field, form.cleaned_data[field])

        objectUpdate.save(update_fields=fields)
        return redirect(self.success_url)

    def form_invalid(self, form):
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
        form.save()

        messages.success(self.request, "Property created successfully!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class PropertyUpdateView(UpdateView):
    model = Property
    form_class = AgentCreatePropertyForm
    template_name = 'components/home/property_form.html'
    success_url = reverse_lazy('home_agent')

    def get_initial(self):
        initial = super().get_initial()
        property = self.get_object()

        if not property.renter_name:
            initial['renter_name'] = "Unknown"

        return initial

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
    template_name = 'components/home/editRenters.html'  # you’ll create this
    success_url = reverse_lazy('manage_renters')  # name of the list view URL

# ################## Create Job Order ##################
@method_decorator(login_required, name='dispatch')
class AgentJobCreateView(CreateView):
    model = Jobs
    form_class = AgentCreateJobForm
    template_name = 'components/home/agent_job_form.html'
    success_url = reverse_lazy('agent_job_create')

    def form_valid(self, form):
        form.instance.agent = AgentRegister.objects.get(user=self.request.user)
        return super().form_valid(form)