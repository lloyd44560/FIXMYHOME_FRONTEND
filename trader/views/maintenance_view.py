from django.views.generic import TemplateView

from trader.models import Jobs
from trader.models import Bidding
from trader.models import TraderRegistration
from trader.models import TraderIndustry

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from trader.decorators.traderOnly import trader_required
from django.shortcuts import render, redirect,get_object_or_404

@method_decorator([login_required, trader_required], name='dispatch')
class MaintenanceView(TemplateView):
    template_name = 'pages/maintenance_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context