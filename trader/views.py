from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from .models import TraderRegistration
from .forms import TraderRegistrationForm, TeamMemberFormSet, TraderEditProfileForm

# View for the registration page
class TraderRegistrationCreateView(CreateView):
    model = TraderRegistration
    form_class = TraderRegistrationForm
    template_name = 'pages/register.html'
    success_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formset = TeamMemberFormSet()
        return render(request, self.template_name, {'form': form, 'formset': formset})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        formset = TeamMemberFormSet(request.POST)
        print("Form errors:", form.errors)
        print("Formset errors:", formset.errors)
        if form.is_valid() and formset.is_valid():
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

            formset.instance = trader
            formset.save()
            
            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {'form': form, 'formset': formset})

# View for the home page
@method_decorator(login_required, name='dispatch')
class TraderHomeView(TemplateView):
    template_name = 'pages/home.html'

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
        print('Form Errors', form.errors)
        context['error'] = "There was an error updating your profile."
        return self.render_to_response(context)