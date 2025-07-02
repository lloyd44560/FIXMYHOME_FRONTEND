from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.utils.timezone import now
from django.urls import reverse_lazy

from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic.edit import UpdateView, FormView
from django.contrib.auth.models import User

from .models import TraderRegistration, TeamMember, ContractorLicense
from .models import Jobs
from agent.models import AgentRegister
from .forms import TraderRegistrationForm, TeamMemberFormSet
from .forms import ContractorLicenseSet, TraderEditProfileForm
from .forms import JobScheduleForm

# View for the registration page
class TraderRegistrationCreateView(CreateView):
    model = TraderRegistration
    form_class = TraderRegistrationForm
    template_name = 'pages/register.html'
    success_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formset = TeamMemberFormSet()
        form_license = ContractorLicenseSet()
        return render(request, self.template_name, {
            'form': form, 
            'formset': formset, 
            'formLicense': form_license
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        formset = TeamMemberFormSet(request.POST)
        form_license = ContractorLicenseSet(request.POST)
        
        if form.is_valid() and formset.is_valid() and form_license.is_valid():
            # Duplicate username or email check
            username = form.cleaned_data['name']
            email = form.cleaned_data['email']

            if User.objects.filter(username=username).exists():
                form.add_error('name', 'Username already exists.')
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Email already exists.')

            if form.errors:
                # Return with form errors due to duplicates
                return render(request, self.template_name, {'form': form, 'formset': formset})
        
            trader = form.save(commit=False)
            user = User.objects.create_user(
                username=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                is_staff=1
            )
            trader.user = user
            trader.password = None
            trader.save()

            # ✅ Now loop the team member lists
            team_names = request.POST.getlist('team_name')
            team_positions = request.POST.getlist('team_position')
            form_data = formset.cleaned_data[0]

            for name, position in zip(team_names, team_positions):
                TeamMember.objects.create(
                    trader=trader, # <--- FK relation
                    teamName=name,
                    position=position,  
                    labour_rate_per_hour = form_data['labour_rate_per_hour'],
                    callout_rate = form_data['callout_rate'],
                    contact_number = form_data['contact_number'],
                    active_postal_codes = form_data['active_postal_codes'],
                    holidays = form_data['holidays'],
                    time_in = form_data['time_in'],
                    time_out = form_data['time_out'],
                    IsWorkInHoliday = form_data['IsWorkInHoliday'],
                    holidayTime_in = form_data['holidayTime_in'],
                    holidayTime_out = form_data['holidayTime_out']
                )
            
            # ✅ Now loop the contract license lists
            license_number = request.POST.getlist('license_number')

            for licenses in license_number:
                ContractorLicense.objects.create(
                    trader=trader, # <--- FK relation
                    contractorLicense=licenses
                )
            
            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {'form': form, 'formset': formset})

# View for the home page
@method_decorator(login_required, name='dispatch')
class TraderHomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Count by status & priority
        context['to_quote_urgent'] = Jobs.objects.filter(status='quoted', priority=True).count()
        context['to_quote_non_urgent'] = Jobs.objects.filter(status='quoted', priority=False).count()

        context['pending_urgent'] = Jobs.objects.filter(status='confirmed', priority=True).count()
        context['pending_non_urgent'] = Jobs.objects.filter(status='confirmed', priority=False).count()

        context['approved_urgent'] = Jobs.objects.filter(status='approved', priority=True).count()
        context['approved_non_urgent'] = Jobs.objects.filter(status='approved', priority=False).count()

        # Jobs Today (scheduled today)
        today = now().date()
        context['today_urgent'] = Jobs.objects.filter(scheduled_at__date=today, priority=True).count()
        context['today_non_urgent'] = Jobs.objects.filter(scheduled_at__date=today, priority=False).count()
        
        return context

@method_decorator(login_required, name='dispatch')
class TraderProfileView(UpdateView):
    model = TraderRegistration
    form_class = TraderEditProfileForm
    template_name = 'components/home/navigatorPages/viewProfileTrader.html'
    success_url = reverse_lazy('profile_trader')

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
        trader = self.get_object()

        if trader:
            context['full_name'] = user.get_full_name() or trader.name
            context['email'] = user.email or trader.email
            context['phone'] = trader.phone
            context['address'] = trader.address_line_1
            context['addressTwo'] = trader.address_line_2

        else:
            context['error'] = "Trader profile not found."

        return context
    
    def form_valid(self, form):
        objectUpdate = self.get_object()

        # Fields to update
        fields = [
            'name', 'email', 'phone', 'company_type', 'company_name', 'company_address',
            'company_email', 'company_landline', 'contractor_license', 'abn',
            'industry', 'other_expertise', 'state', 'municipality', 'city',
            'postal_code', 'address_line_1', 'address_line_2',
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
class TraderEditSecurityView(FormView):
    template_name = "components/home/navigatorPages/editSecurityTrader.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profile_trader')

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

@method_decorator(login_required, name='dispatch')
class JobListView(ListView):
    model = Jobs
    template_name = 'components/home/job_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        queryset = super().get_queryset()

        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')  # 'true' or 'false'

        if status:
            queryset = queryset.filter(status=status)
        if priority == 'true':
            queryset = queryset.filter(priority=True)
        elif priority == 'false':
            queryset = queryset.filter(priority=False)

        # Order priority=True first, then by quoted_at descending
        return queryset.order_by('-priority', '-quoted_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['status_options'] = dict(Jobs._meta.get_field('status').choices)

        return context