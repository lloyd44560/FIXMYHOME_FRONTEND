from django.db import models
from django.urls import reverse

from trader.models import TraderRegistration

class TraderNotification(models.Model):
    trader_id = models.ForeignKey(TraderRegistration, on_delete=models.CASCADE, null=True, blank=True, related_name='trader_notifs')

    email_references = models.CharField(max_length=255, blank=True, null=True)
    email_notifications = models.BooleanField(default=True)
    job_alerts = models.BooleanField(default=False)
    feedback_requests = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)
    priority = models.BooleanField(default=False)
    message_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notifications for {self.trader_id.name}"
