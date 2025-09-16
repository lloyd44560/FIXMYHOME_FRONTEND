from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone

from trader.models import Bidding
from trader.models import TraderNotification
from agent.models import AgentRegister
from agent.forms import BiddingApprovalForm

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class BiddingApprovalView(UserPassesTestMixin, UpdateView):
    model = Bidding
    form_class = BiddingApprovalForm
    template_name = 'pages/bidding_approval.html'
    success_url = reverse_lazy('agent_bid_list')

    def test_func(self):
        # Only allow agents to approve
        return hasattr(self.request.user, 'agentregister')

    def form_valid(self, form):
        agent = AgentRegister.objects.filter(user=self.request.user).first()
        bidding = form.save(commit=False)
        
        # Create a notification to Trader
        if not bidding.is_approved: # Rejected
            print('Rejected Bid')
            print(bidding.trader, 'Trader')
            TraderNotification.objects.create(
                trader_id=bidding.trader, 
                message_description=f"Unfortunately, your quotation on '{bidding.jobs.job_code}' was not selected."
            )
        elif bidding.is_approved: # Approved
            print('Approved Bid')
            TraderNotification.objects.create(
                trader_id=bidding.trader, 
                message_description=f"Congratulations! Your quotation on '{bidding.jobs.job_code}' was approved."
            )
            bidding.approved_at = timezone.now()
            bidding.approved_by = agent

        bidding.save()
        messages.success(self.request, 'Bid approval status updated.')
        return super().form_valid(form)