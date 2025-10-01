
from django.utils import timezone
from django.views.generic import TemplateView

from trader.models import Jobs
from trader.models import Bidding
from trader.models import TraderRegistration

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from trader.decorators.traderOnly import trader_required

# View for the home page
@method_decorator([login_required, trader_required], name='dispatch')
class TraderHomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ Get the trader linked to the logged-in user
        trader = TraderRegistration.objects.filter(user=self.request.user).first()

        # Count by status & priority
        context['to_quote_urgent'] = Bidding.objects.filter(
            jobs__priority=True, 
            trader_id=trader, 
            is_active=True
        ).count()
        context['to_quote_non_urgent'] = Bidding.objects.filter(
            jobs__priority=False, 
            trader_id=trader, 
            is_active=True
        ).count()

        context['pending_urgent'] = Bidding.objects.filter(
            is_approved=None, 
            jobs__priority=True, 
            trader_id=trader,
            is_active=True
        ).count()
        context['pending_non_urgent'] = Bidding.objects.filter(
            is_approved=None, 
            jobs__priority=False, 
            trader_id=trader,
            is_active=True
        ).count()

        context['approved_urgent'] = Jobs.objects.filter(
            status='approved', 
            priority=True, 
            trader_id=trader
        ).count()
        context['approved_non_urgent'] = Jobs.objects.filter(
            status='approved', 
            priority=False, 
            trader_id=trader
        ).count()

        # Jobs Today (scheduled today)
        context['today_urgent'] = Jobs.objects.filter(
            scheduled_at=timezone.now().date(), 
            priority=True, 
            trader_id=trader
        ).count()
        context['today_non_urgent'] = Jobs.objects.filter(
            scheduled_at=timezone.now().date(),
            priority=False, 
            trader_id=trader
        ).count()
                
        return context