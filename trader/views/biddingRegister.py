from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import CreateView

from trader.models import TraderRegistration
from trader.models import Bidding
from trader.forms import BiddingForm

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from trader.decorators.traderOnly import trader_required


class BiddingCreateView(LoginRequiredMixin, CreateView):
    model = Bidding
    form_class = BiddingForm
    template_name = 'pages/bidding_create.html'
    success_url = reverse_lazy('bidding_create')  # Redirect to job list or bidding list

    def form_valid(self, form):
        # Set trader as current user
        trader = TraderRegistration.objects.filter(user=self.request.user).first()
        form.instance.trader = trader

        # Use form.instance (not bidding yet)
        job = form.instance.jobs  

        # Check for duplicates
        if Bidding.objects.filter(trader=trader, jobs=job).exists():
            messages.error(self.request, "You have already submitted a quotation for this job.")
            return self.form_invalid(form)

        # Save the bidding first
        bidding = form.save()

        # Send email to agent (or trader depending on your logic)
        send_mail(
            subject=f"New Quotation Submitted - {bidding.jobs.job_code}",
            message=f"Hi {bidding.jobs.agent.name},\n\n"
                    f"A new quotation has been submitted by {trader.name} "
                    f"for Job {bidding.jobs.job_code}. Please review it.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[bidding.jobs.agent.user.email or bidding.jobs.agent.email],  # email to agent
            fail_silently=False,
        )
        
        messages.success(self.request, "Your quotation has been submitted successfully and is now pending agent review.")
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only filter team_member by trader, not jobs
        trader = TraderRegistration.objects.filter(user=self.request.user).first()
        form.fields['team_member'].queryset = form.fields['team_member'].queryset.filter(trader=trader)
        return form