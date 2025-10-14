from django.urls import reverse_lazy
from django.conf import settings
from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone
from django.shortcuts import redirect
from django.core.mail import send_mail

from trader.models import Bidding
from trader.models import TraderNotification
from agent.models import AgentRegister
from agent.forms import BiddingApprovalForm

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required
from django.contrib.auth.models import User
from chat.models import Message

from renter.models import Renter

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

        # Example: update related Job status
        job = bidding.jobs

        # Create a notification to Trader
        if not bidding.is_approved:  # Rejected
            TraderNotification.objects.create(
                trader_id=bidding.trader,
                subject=(
                    f"Unfortunately, your quotation on '{bidding.jobs.job_code}' "
                    "was not selected."
                ),
                message_description=bidding.approval_notes
            )

            # Example: Send rejection email (optional)
            send_mail(
                subject="Quotation Result",
                message=f"Hi {bidding.trader.name},\n\n"
                        f"Unfortunately, your quotation on '{bidding.jobs.job_code}' "
                        f"was not selected.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[bidding.trader.email],
            )

        elif bidding.is_approved:  # Approved
            TraderNotification.objects.create(
                trader_id=bidding.trader,
                subject=(f"Congratulations! Your quotation on '{bidding.jobs.job_code}' "
                    "was approved."),
                message_description=bidding.approval_notes
            )

            # trigger a conversation between the users
            try:
                renter_obj = Renter.objects.filter(name=bidding.jobs.renter).first()
                trader_user = User.objects.filter(email=bidding.trader.email).first()

                if renter_obj and renter_obj.user:
                    job_code = bidding.jobs.job_code or "N/A"
                    message_content = (
                        f"Hi {renter_obj.name}, this is {bidding.trader.name}. "
                        f"I’ve accepted your job request with Job Order No. <b>{job_code}</b>. "
                        "I’ll be in touch soon to coordinate further details. Thank you!"
                    )

                    Message.objects.create(
                        sender=trader_user,
                        receiver=renter_obj.user,
                        content=message_content
                    )

            except Renter.DoesNotExist:
                renter_obj = None

            bidding.approved_at = timezone.now()
            bidding.approved_by = agent

            # Fill Job details
            job.status = "approved"
            job.trader = bidding.trader
            job.start_date = bidding.start_date
            job.end_date = bidding.end_date
            job.save()

            # Example: Send approval email
            send_mail(
                subject="Quotation Approved!",
                message=f"Hi {bidding.trader.name},\n\n"
                        f"Congratulations! Your quotation on '{bidding.jobs.job_code}' "
                        f"was approved.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[bidding.trader.email],
            )


        bidding.save()
        messages.success(self.request, 'Bid approval status updated.')
        return super().form_valid(form)