from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from .models import TraderRegistration
from .forms import TraderRegistrationForm, TeamMemberFormSet

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
class TraderProfileView(TemplateView):
    template_name = 'components/home/navigatorPages/viewProfileTrader.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            trader = TraderRegistration.objects.get(user=user)
            context['full_name'] = user.get_full_name() or trader.name
            context['email'] = user.email
        except TraderRegistration.DoesNotExist:
            context['error'] = "Trader profile not found."

        return context