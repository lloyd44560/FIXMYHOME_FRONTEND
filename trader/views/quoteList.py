from django.views.generic import ListView
from trader.models import Bidding
from trader.models import TraderRegistration

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from trader.decorators.traderOnly import trader_required

@method_decorator([login_required, trader_required], name='dispatch')
class QuoteListView(ListView):
    model = Bidding
    template_name = 'pages/quote_list.html'
    context_object_name = 'quotes'

    def get_queryset(self):
        queryset = super().get_queryset()

        # ✅ Get the trader linked to the logged-in user
        trader = TraderRegistration.objects.filter(user=self.request.user).first()

        if trader:
            print(f"Trader ID: {trader.id}, Name: {trader.name}")
            queryset = queryset.filter(trader_id=trader)  # show only trader's jobs
        else:
            queryset = queryset.none()  # if no trader, return empty queryset

        # Filtering
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')  # 'true' or 'false'

        status_map = {"approved": True, "rejected": False, "pending": None}
        
        if status in status_map:
            if status_map[status] is None:
                queryset = queryset.filter(is_approved__isnull=True)
            else:
                queryset = queryset.filter(is_approved=status_map[status])

        if priority == 'true':
            queryset = queryset.filter(jobs__priority=True)
        elif priority == 'false':
            queryset = queryset.filter(jobs__priority=False)

        # Order by created_at descending
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        return context