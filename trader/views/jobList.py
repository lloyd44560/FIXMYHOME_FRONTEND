from django.views.generic import ListView
from trader.models import Jobs
from trader.models import TraderRegistration

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from trader.decorators.traderOnly import trader_required

@method_decorator([login_required, trader_required], name='dispatch')
class JobListView(ListView):
    model = Jobs
    template_name = 'components/home/job_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        queryset = super().get_queryset()

        # ✅ Get the trader linked to the logged-in user
        trader = TraderRegistration.objects.filter(user=self.request.user).first()

        if trader:
            queryset = queryset.filter(trader=trader)  # show only trader's jobs
        else:
            queryset = queryset.none()  # if no trader, return empty queryset

        # Filtering
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')  # 'true' or 'false'

        if status:
            queryset = queryset.filter(status=status)
        if priority == 'true':
            queryset = queryset.filter(priority=True)
        elif priority == 'false':
            queryset = queryset.filter(priority=False)

        # Order priority=True first, then by quoted_at descending
        return queryset.order_by('-priority', '-quoted_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        context['status_options'] = dict(Jobs._meta.get_field('status').choices)
        return context