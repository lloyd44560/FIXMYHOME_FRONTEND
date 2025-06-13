from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from .models import AgentRegister
from .forms import AgentFormClass

# Create your views here.
class AgentRegistrationCreateView(CreateView):
    model = AgentRegister
    form_class = AgentFormClass
    template_name = 'pages/register.html'
    success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        print("Form errors:", form.errors)

        if form.is_valid():
            pass
        else:
            return render(request, self.template_name, {'form': form})