from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.timezone import now

from django.urls import reverse_lazy

from django.core.paginator import Paginator
from django.views.generic import TemplateView
from trader.models import Jobs
from agent.models import AgentRegister, Property

# Middleware decorator
from agent.decorators.agentOnly import agent_required

# View for the home page
@method_decorator([login_required, agent_required], name='dispatch')
class AgentHomeView(TemplateView):
    template_name = 'pages/homeAgent.html'
    success_url = reverse_lazy("home_agent")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get only active properties
        properties_list = Property.objects.filter(is_active=True).order_by('-created_at')

        # Set up pagination
        paginator = Paginator(properties_list, 10)  # Show 10 properties per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['properties'] = page_obj
        context['page_obj'] = page_obj  # For pagination controls

        agent = AgentRegister.objects.get(user=self.request.user)

        # Count by status & priority
        context['to_quote_urgent'] = Jobs.objects.filter(agent=agent, status='quoted', priority=True).count()
        context['to_quote_non_urgent'] = Jobs.objects.filter(agent=agent, status='quoted', priority=False).count()

        context['pending_urgent'] = Jobs.objects.filter(agent=agent, status='confirmed', priority=True).count()
        context['pending_non_urgent'] = Jobs.objects.filter(agent=agent, status='confirmed', priority=False).count()

        context['approved_urgent'] = Jobs.objects.filter(agent=agent, status='approved', priority=True).count()
        context['approved_non_urgent'] = Jobs.objects.filter(agent=agent, status='approved', priority=False).count()

        # Jobs Today (scheduled today)
        today = now().date()
        context['today_urgent'] = Jobs.objects.filter(agent=agent, scheduled_at__date=today, priority=True).count()
        context['today_non_urgent'] = Jobs.objects.filter(agent=agent, scheduled_at__date=today, priority=False).count()

        return context