from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from functools import wraps
from agent.models.registerAgent import AgentRegister

def agent_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        agent = AgentRegister.objects.filter(user=request.user).first()
        if not agent:
            return PermissionDenied("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper