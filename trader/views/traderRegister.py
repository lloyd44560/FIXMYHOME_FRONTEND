from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.views.generic import CreateView
from django.contrib.auth.models import User

from trader.models import TraderRegistration, TeamMember, ContractorLicense, TraderIndustry
from trader.forms import TraderRegistrationForm, TeamMemberFormSet
from trader.forms import ContractorLicenseSet

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

            # ✅ Now get Holiday lists
            holidays = request.POST.getlist('holiday_date')
            for name, position in zip(team_names, team_positions):
                TeamMember.objects.create(
                    trader=trader, # <--- FK relation
                    teamName=name,
                    position=position,  
                    labour_rate_per_hour = form_data['labour_rate_per_hour'],
                    callout_rate = form_data['callout_rate'],
                    contact_number = form_data['contact_number'],
                    active_postal_codes = form_data['active_postal_codes'],
                    holidays = holidays,  # Store as JSON
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

            # ✅ Now loop the expertise lists
            expertise = request.POST.getlist('industry_expertise')

            for exp in expertise:
                TraderIndustry.objects.create(
                    trader=trader,  # <--- FK relation
                    industry=exp
                )

            return redirect(self.success_url)
        else:
            print(f"Form errors: {form.errors}, Formset errors: {formset.errors}, License errors: {form_license.errors}")
            return render(request, self.template_name, {'form': form, 'formset': formset})