from django.shortcuts import render
from django.views.generic import CreateView
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
            
            return reverse_lazy('login')
        else:
            return render(request, self.template_name, {'form': form, 'formset': formset})