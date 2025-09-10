from django.urls import reverse
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.views.generic import ListView
from trader.models import Jobs
from trader.models.servicesTrader import Services

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class ActiveJobsListView(ListView):
    model = Jobs
    template_name = 'components/home/active_jobs_list.html'
    context_object_name = 'jobs'
    paginate_by = 10  # Adjust as needed

    def post(self, request, *args, **kwargs):
        # Extract filter parameters from POST
        params = {
            'page': '1',  # Force page to 1
            'status': request.POST.get('status', ''),
            'category': request.POST.get('category', ''),
            'priority': request.POST.get('priority', ''),
            'trader': request.POST.get('trader', ''),
            'scheduled_at': request.POST.get('scheduled_at', '')
        }
        # Redirect to GET with page=1 and filter parameters
        return HttpResponseRedirect(f"{reverse('active_jobs_list')}?{urlencode(params)}")

    def get(self, request, *args, **kwargs):
        try:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            return self.render_to_response(context)
        except self.paginator.InvalidPage:
            # Redirect to page 1 if the requested page is invalid
            params = request.GET.copy()
            params['page'] = '1'
            return HttpResponseRedirect(f"{reverse('active_jobs_list')}?{params.urlencode()}")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter only active jobs
        queryset = queryset.filter(is_active=True)

        # Get filter parameters from request.POST or request.GET
        status = self.request.POST.get('status') if self.request.method == 'POST' else self.request.GET.get('status')
        category = self.request.POST.get('category') if self.request.method == 'POST' else self.request.GET.get('category')
        priority = self.request.POST.get('priority') if self.request.method == 'POST' else self.request.GET.get('priority')
        trader = self.request.POST.get('trader') if self.request.method == 'POST' else self.request.GET.get('trader')
        scheduled_at = self.request.POST.get('scheduled_at') if self.request.method == 'POST' else self.request.GET.get('scheduled_at')

        # Apply filters if provided
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category=category)
        if trader:
            queryset = queryset.filter(trader__name__icontains=trader)
        if scheduled_at:
            queryset = queryset.filter(scheduled_at=scheduled_at)
        if priority == 'true':
            queryset = queryset.filter(priority=True)
        elif priority == 'false':
            queryset = queryset.filter(priority=False)
        return queryset.order_by('-priority', '-scheduled_at', '-approved_at', '-confirmed_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Preserve filter values for form repopulation
        category = self.request.POST.get('category', '')
        if self.request.method == 'POST':
            context['filter_status'] = self.request.POST.get('status', '')
            context['filter_category'] = int(category) if category and category.isdigit() else ''
            context['filter_priority'] = self.request.POST.get('priority', '')
            context['filter_trader'] = self.request.POST.get('trader', '')
            context['filter_scheduled_at'] = self.request.POST.get('scheduled_at', '')
        else:
            context['filter_status'] = self.request.GET.get('status', '')
            context['filter_category'] = self.request.GET.get('category', '')
            context['filter_priority'] = self.request.GET.get('priority', '')
            context['filter_trader'] = self.request.GET.get('trader', '')
            context['filter_scheduled_at'] = self.request.GET.get('scheduled_at', '')

        # Status and category options for form
        context['status_options'] = dict(self.model._meta.get_field('status').choices)
        context['category_options'] = {
            service.id: service.description
            for service in Services.objects.all()
        }
        return context