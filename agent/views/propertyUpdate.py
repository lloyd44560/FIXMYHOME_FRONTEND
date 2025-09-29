from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.views.generic.edit import UpdateView
from django.contrib import messages
from agent.models import Property
from agent.forms import AgentCreatePropertyForm

# Middleware decorator
from django.utils.decorators import method_decorator
from agent.decorators.agentOnly import agent_required
from django.contrib.auth.decorators import login_required

@method_decorator([login_required, agent_required], name='dispatch')
class PropertyUpdateView(UpdateView):
    model = Property
    form_class = AgentCreatePropertyForm
    template_name = 'components/home/property_form.html'
    success_url = reverse_lazy('manage_properties')

    def get_initial(self):
        initial = super().get_initial()
        property = self.get_object()
        if hasattr(property, 'renter') and property.renter:
            initial['renter_name'] = property.renter.name
        else:
            initial['renter_name'] = ""
        return initial

    def form_valid(self, form):
        property = form.save(commit=False)
        # Set the renter FK from the validated renter_name field
        if hasattr(form, 'cleaned_data') and 'renter_name' in form.cleaned_data:
            from renter.models import Renter
            renter_name = form.cleaned_data['renter_name']
            renter_qs = Renter.objects.filter(name__iexact=renter_name)
            if renter_qs.exists():
                property.renter = renter_qs.first()
          # Update property manager
        property.property_manager = form.cleaned_data.get('property_manager')
        property.save()
        messages.success(self.request, 'Property details updated successfully.')
        return redirect(self.success_url)