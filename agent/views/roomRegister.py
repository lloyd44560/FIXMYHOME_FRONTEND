from django.urls import reverse_lazy

from django.views.generic import CreateView
from django.contrib import messages
from agent.models import Property, Rooms
from agent.forms import AgentCreateRoomForm

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class RoomCreateView(CreateView):
    model = Rooms
    form_class = AgentCreateRoomForm
    template_name = 'components/home/property_detail.html'

    def form_valid(self, form):
        property_instance = get_object_or_404(Property, pk=self.kwargs['property_id'])
        form.instance.property = property_instance
        form.instance.renter = property_instance.renter or None  # Set renter from property
        messages.success(self.request, "Room created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create room. Please check the form.")
        return reverse_lazy('property_view', pk=self.kwargs['property_id'])

    def get_success_url(self):
        return reverse_lazy('property_view', kwargs={'pk': self.kwargs['property_id']})