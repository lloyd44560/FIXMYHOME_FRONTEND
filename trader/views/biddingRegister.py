from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import CreateView

from trader.models import TraderRegistration
from trader.models import TeamMember, ItemNeeded
from trader.models import Bidding, Jobs
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
        bidding = form.save(commit=False)

        if bidding.end_date < bidding.start_date:
            messages.error(self.request, "End date cannot be earlier than start date.")
            return self.form_invalid(form)

        bidding.trader = trader

        # Use form.instance (not bidding yet)
        job = bidding.jobs  

        # Check for duplicates
        if Bidding.objects.filter(trader=trader, jobs=job).exists():
            messages.error(self.request, "You have already submitted a quotation for this job.")
            return self.form_invalid(form)
        
        # Auto-assign team member
        if trader.isTeamMember:
            team_member = TeamMember.objects.filter(user=self.request.user).first()
            form.instance.team_member = team_member

        # Save the bidding first
        bidding.save()
        form.save_m2m()

        # Save dynamic items
        item_names = self.request.POST.getlist('item_name[]')
        item_prices = self.request.POST.getlist('item_price[]')

        for name, price in zip(item_names, item_prices):
            if name.strip():
                try:
                    price_val = float(price) if price else 0.0
                except ValueError:
                    price_val = 0.0
                ItemNeeded.objects.create(bidding=bidding, name=name.strip(), price=price_val)

        # Increment job bid count
        job.bid_count += 1
        job.save()

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        trader = TraderRegistration.objects.filter(user=self.request.user).first()
        kwargs['trader'] = trader
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trader = TraderRegistration.objects.filter(user=self.request.user).first()
        val = trader.isDirector or trader.isAdmin if trader else False
        # Add flag for template condition
        context['is_director'] = val
        context['memberName'] = trader.name if trader else ''

        # ✅ Filter only quoted + open jobs and order DESC by quoted_at or id
        context['jobs_filtered'] = Jobs.objects.filter(
            trader=trader,
            bid_status='open',
            status='quoted'
        ).order_by('-quoted_at')
        
        # Filter team members by trader if director
        if trader.isDirector:
            team_member_val = TeamMember.objects.filter(trader_id=trader)
        context['team_member_filtered'] = team_member_val or TeamMember.objects.none()

        return context