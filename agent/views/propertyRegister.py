from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.views.generic import CreateView
from django.contrib import messages
from agent.models import AgentRegister, Property
from agent.forms import AgentCreatePropertyForm

# Middleware decorator
from django.utils.decorators import method_decorator
from agent.decorators.agentOnly import agent_required
from django.contrib.auth.decorators import login_required

@method_decorator([login_required, agent_required], name='dispatch')
class PropertyCreateView(CreateView):
    template_name = "components/home/property_form.html"
    model = Property
    form_class = AgentCreatePropertyForm
    success_url = reverse_lazy("home_agent")

    def form_valid(self, form):
        userAgent = AgentRegister.objects.get(user=self.request.user)
        property = form.save(commit=False)
        property.agent = userAgent
        # Set the renter FK from the validated renter_name field
        if hasattr(form, 'cleaned_data') and 'renter_name' in form.cleaned_data:
            from renter.models import Renter
            renter_name = form.cleaned_data['renter_name']
            renter_qs = Renter.objects.filter(name__iexact=renter_name)
            if renter_qs.exists():
                property.renter = renter_qs.first()
        
        # Set property manager
        property.property_manager = form.cleaned_data.get('property_managers')

        property.save()
        messages.success(self.request, "Property created successfully!")
        return redirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))