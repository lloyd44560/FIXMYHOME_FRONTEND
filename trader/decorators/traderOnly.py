from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from functools import wraps

from trader.models import TraderRegistration
from trader.models import TeamMember

def trader_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        trader = TraderRegistration.objects.filter(user=request.user).first()
        team_member = TeamMember.objects.filter(user=request.user).first()
        if not trader and not team_member:
            return PermissionDenied("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper