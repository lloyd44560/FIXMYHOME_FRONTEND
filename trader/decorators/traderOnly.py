from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from functools import wraps

from trader.models.registerTrader import TraderRegistration

def trader_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        trader = TraderRegistration.objects.filter(user=request.user).first()
        if not trader:
            return PermissionDenied("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper