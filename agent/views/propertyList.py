from django.urls import reverse
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.views.generic import ListView
from agent.models import Property

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class PropertiesListView(ListView):
    model = Property
    template_name = 'components/home/propertiesList.html'
    context_object_name = 'properties'
    paginate_by = 10  # Adjust as needed

    def post(self, request, *args, **kwargs):
        # Extract filter parameters from POST
        params = {
            'page': '1',  # Force page to 1
            'status': request.POST.get('status', ''),
            'address': request.POST.get('address', ''),
            'renter': request.POST.get('renter', '')
        }
        # Redirect to GET with page=1 and filter parameters
        return HttpResponseRedirect(f"{reverse('manage_properties')}?{urlencode(params)}")

    def get(self, request, *args, **kwargs):
        try:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            return self.render_to_response(context)
        except self.paginator.InvalidPage:
            # Redirect to page 1 if the requested page is invalid
            params = request.GET.copy()
            params['page'] = '1'
            return HttpResponseRedirect(f"{reverse('manage_properties')}?{params.urlencode()}")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter only active properties
        queryset = queryset.filter(is_active=True)

        # Get filter parameters from request.POST or request.GET
        status = self.request.POST.get('status') if self.request.method == 'POST' else self.request.GET.get('status')
        address = self.request.POST.get('address') if self.request.method == 'POST' else self.request.GET.get('address')
        renter = self.request.POST.get('renter') if self.request.method == 'POST' else self.request.GET.get('renter')

        # Apply filters if provided
        if status:
            queryset = queryset.filter(status=status)
        if address:
            queryset = queryset.filter(address__icontains=address)
        if renter:
            queryset = queryset.filter(renter__name__icontains=renter)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Preserve filter values for form repopulation
        if self.request.method == 'POST':
            context['filter_status'] = self.request.POST.get('status', '')
            context['filter_address'] = self.request.POST.get('address', '')
            context['filter_renter'] = self.request.POST.get('renter', '')
        else:
            context['filter_status'] = self.request.GET.get('status', '')
            context['filter_address'] = self.request.GET.get('address', '')
            context['filter_renter'] = self.request.GET.get('renter', '')
        return context