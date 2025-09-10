
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib import messages

from renter.models import Renter
from agent.forms import RenterUpdateForm

# Middleware decorator
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class RenterUpdateView(UpdateView):
    model = Renter
    form_class = RenterUpdateForm
    template_name = 'components/home/editRenters.html'
    success_url = reverse_lazy('manage_renters')

    def get_object(self, queryset=None):
        # Get the renter object by pk from the URL
        pk = self.kwargs.get('pk')
        return get_object_or_404(Renter, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['renter'] = self.get_object()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Renter updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the renter.')
        return self.render_to_response(self.get_context_data(form=form))