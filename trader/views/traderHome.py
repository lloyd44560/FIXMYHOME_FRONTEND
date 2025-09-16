
from django.utils.timezone import now
from django.views.generic import TemplateView

from trader.models import Jobs
from trader.models import TraderNotification

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

        # Count by status & priority
        context['to_quote_urgent'] = Jobs.objects.filter(status='quoted', priority=True).count()
        context['to_quote_non_urgent'] = Jobs.objects.filter(status='quoted', priority=False).count()

        context['pending_urgent'] = Jobs.objects.filter(status='confirmed', priority=True).count()
        context['pending_non_urgent'] = Jobs.objects.filter(status='confirmed', priority=False).count()

        context['approved_urgent'] = Jobs.objects.filter(status='approved', priority=True).count()
        context['approved_non_urgent'] = Jobs.objects.filter(status='approved', priority=False).count()

        # Jobs Today (scheduled today)
        today = now().date()
        context['today_urgent'] = Jobs.objects.filter(scheduled_at__date=today, priority=True).count()
        context['today_non_urgent'] = Jobs.objects.filter(scheduled_at__date=today, priority=False).count()

        # Base unread notifications
        unread_qs = TraderNotification.objects.filter(
            trader_id__user=self.request.user,  # join through TraderRegistration
            seen=False
        ).order_by("-created_at")

        # Notifications for Trader
        context["unread_messages"] = unread_qs
        context["unread_count"] = unread_qs.count()
                
        return context