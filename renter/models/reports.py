from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
from renter.models import Renter
from agent.models.registerAgent import AgentRegister

class EmailVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} — {self.token}"

class MinimumStandardReport(models.Model):
    renter = models.ForeignKey('renter.Renter', on_delete=models.CASCADE)
    tenant_name = models.CharField(max_length=255)
    audit_no = models.CharField(max_length=100)
    auditor = models.CharField(max_length=255)
    inspection_address = models.TextField()
    managing_agent = models.CharField(max_length=255)
    audit_date = models.DateField()
    room = models.CharField(max_length=255)
    comments = models.TextField(null=True, blank=True)
    report_file = models.FileField(upload_to='standard_reports/', null=True, blank=True)

    company = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    audit_expiry = models.DateField(null=True, blank=True)


# Added for Renter request for reports by Agent
class RequestReport(models.Model):
    REPORT_CHOICES = [
        ('maintenance', 'Maintenance Request Report'),
        ('condition', 'Condition Report'),
        ('appliance', 'Appliance Report'),
        ('minimum_standard', 'Minimum Standard Reports'),
    ]

    report_type = models.CharField(
        max_length=50,
        choices=REPORT_CHOICES,
        verbose_name="Type of Report"
    )
    reason = models.CharField(max_length=255, blank=True, null=True)
    date_requested = models.DateTimeField(default=timezone.now)

    renter = models.ForeignKey(
        Renter,
        on_delete=models.CASCADE,
        related_name='request_reports'
    )
    agent = models.ForeignKey(
        AgentRegister,
        on_delete=models.CASCADE,
        related_name='request_reports'
    )

    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent',
        verbose_name="Status"
    )


    def __str__(self):
        return f"{self.get_report_type_display()} by {self.renter} ({self.date_requested.strftime('%Y-%m-%d')})"


class Event(models.Model):
    title = models.CharField(max_length=200)
    start = models.DateField()
    end = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title