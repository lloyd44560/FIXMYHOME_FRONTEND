from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from django.contrib import messages
from agent.models import Property

# Middleware decorator
from django.shortcuts import get_object_or_404
from agent.decorators.agentOnly import agent_required

import logging
logger = logging.getLogger(__name__)

@require_POST
@agent_required
# @property_owner_required  # Ensures only the owner or superuser can delete
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property_name = property.name  # Store name before deletion
    try:
        property.delete()
        messages.success(request, f"Property '{property_name}' deleted.")
    except Exception as e:
        messages.error(request, "Failed to delete property. Please try again.")
        logger.error(f"Error deleting property {pk}: {e}")
    return redirect('home_agent')

@require_POST
@agent_required
# @property_owner_required  # Ensures only the owner or superuser can archive
def archive_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    try:
        property.is_active = False
        property.save()
        messages.success(request, f"Property '{property.name}' has been archived.")
    except Exception as e:
        messages.error(request, "Failed to archive property. Please try again.")
        logger.error(f"Error archiving property {pk}: {e}")
    return redirect('home_agent')