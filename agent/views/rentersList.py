from django.urls import reverse
from urllib.parse import urlencode
from django.http import HttpResponseRedirect
from django.views.generic import ListView

from renter.models import Renter

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class RenterListView(ListView):
    model = Renter
    template_name = 'components/home/manageRenters.html'
    context_object_name = 'renters'
    paginate_by = 10  # Adjust as needed

    def post(self, request, *args, **kwargs):
        # Extract filter parameters from POST
        params = {
            'page': '1',  # Force page to 1
            'renter_name': request.POST.get('renter_name', '')
        }
        # Redirect to GET with page=1 and filter parameters
        return HttpResponseRedirect(f"{reverse('manage_renters')}?{urlencode(params)}")

    def get(self, request, *args, **kwargs):
        try:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            return self.render_to_response(context)
        except self.paginator.InvalidPage:
            # Redirect to page 1 if the requested page is invalid
            params = request.GET.copy()
            params['page'] = '1'
            return HttpResponseRedirect(f"{reverse('manage_renters')}?{params.urlencode()}")

    def get_queryset(self):
        queryset = super().get_queryset()
        # Get filter parameters from request.POST or request.GET
        renter_name = self.request.POST.get('renter_name') if self.request.method == 'POST' else self.request.GET.get('renter_name')

        # Apply filters if provided
        if renter_name:
            queryset = queryset.filter(name__icontains=renter_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Preserve filter values for form repopulation
        if self.request.method == 'POST':
            context['filter_renter'] = self.request.POST.get('renter_name', '')
        else:
            context['filter_renter'] = self.request.GET.get('renter_name', '')
        return context