from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.views.generic import TemplateView, ListView, DetailView

from trader.models import Jobs
from trader.models import TraderNotification

# Middlewares
from django.shortcuts import get_object_or_404
from agent.decorators.agentOnly import agent_required

import logging
logger = logging.getLogger(__name__)

# Fetch unread notifications
def get_unread_notifications(user):
    """
    Fetch unread notifications for the given user.
    Returns a queryset (can be used in views, context processors, APIs).
    """
    try:
        return TraderNotification.objects.filter(
            trader_id__user=user,
            seen=False
        ).order_by("-created_at")
        
    except Exception as e:
        logger.error(f"Error fetching notifications! {e}")
        return TraderNotification.objects.none()

class NotificationListView(LoginRequiredMixin, ListView):
    model = TraderNotification
    template_name = "pages/traderNotification/notification_list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return TraderNotification.objects.filter(
            trader_id__user=self.request.user
        ).order_by("-created_at")


class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = TraderNotification
    template_name = "pages/traderNotification/notification_detail.html"
    context_object_name = "notification"

    def get_queryset(self):
        return TraderNotification.objects.filter(
            trader_id__user=self.request.user
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.seen:
            obj.seen = True
            obj.save()
        return obj