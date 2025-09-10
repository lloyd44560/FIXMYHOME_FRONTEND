from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone

from trader.models import Bidding
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
        bidding = form.save(commit=False)
        bidding.approved_at = timezone.now()
        bidding.approved_by = AgentRegister.objects.filter(user=self.request.user).first()
        bidding.save()
        messages.success(self.request, 'Bid approval status updated.')
        return super().form_valid(form)