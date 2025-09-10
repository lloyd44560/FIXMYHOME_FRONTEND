from django.views.generic import ListView
from trader.models import Bidding

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class AgentBidListView(ListView):
    model = Bidding
    template_name = 'components/home/agent_bid_list.html'
    context_object_name = 'bids'

    def get_queryset(self):
        # Show all jobs, ordered by priority and scheduled/approved/confirmed date
        queryset = super().get_queryset()

        # Filter only active properties
        queryset = queryset.filter(is_active=True)

        # Get filter parameters from request
        trader = self.request.GET.get('trader')
        is_approved = self.request.GET.get('status')
        approved_at = self.request.GET.get('approved_at')

        # Apply filters if provided
        if trader:
            queryset = queryset.filter(trader__name__icontains=trader)
        if approved_at:
            queryset = queryset.filter(approved_at=approved_at)

        if is_approved == 'true':
            queryset = queryset.filter(is_approved=True)
        elif is_approved == 'false':
            queryset = queryset.filter(is_approved=False)
        elif is_approved == '':
            queryset = queryset.filter(is_approved__isnull=True)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_options'] = {
            '': 'Pending',
            'true': 'Approved',
            'false': 'Rejected',
        }

        # Preserve filter values in template for form repopulation
        context['filter_trader'] = self.request.GET.get('trader', '')
        context['filter_is_approved'] = self.request.GET.get('status', '')
        context['filter_approved_at'] = self.request.GET.get('approved_at', '')

        return context