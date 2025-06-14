from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from .models import AgentRegister
from .forms import AgentFormClass

# Create your views here.
class AgentRegistrationCreateView(CreateView):
    model = AgentRegister
    form_class = AgentFormClass
    template_name = 'pages/registerAgent.html'
    success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        print("Form errors:", form.errors)

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
class AgentHomeView(TemplateView):
    template_name = 'pages/homeAgent.html'