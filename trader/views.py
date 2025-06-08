from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from .models import TraderRegistration
from .forms import TraderRegistrationForm

# View for the registration page
class TraderRegistrationCreateView(CreateView):
    model = TraderRegistration
    form_class = TraderRegistrationForm
    template_name = 'pages/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Create the auth user
        user = User.objects.create_user(
            username=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        # link the user to TraderRegistration if you have a user field
        form.instance.user = user
        return super().form_valid(form)