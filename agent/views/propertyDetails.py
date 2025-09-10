from django.views.generic.detail import DetailView
from trader.models import Jobs
from agent.models import Property
from agent.forms import AgentCreateJobForm, AgentCreateRoomForm

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class PropertyDetailView(DetailView):
    model = Property
    template_name = 'components/home/property_detail.html'
    context_object_name = 'property'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_form'] = AgentCreateRoomForm()
        context['job_form'] = AgentCreateJobForm()
        context['jobs'] = Jobs.objects.filter(property=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.get(request, *args, **kwargs)