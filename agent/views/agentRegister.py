from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.core.mail import send_mail

from django.conf import settings
from django.urls import reverse_lazy

from django.views.generic import CreateView
from django.contrib.auth.models import User
from agent.models import AgentRegister
from agent.forms import CreateAgentFormClass

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