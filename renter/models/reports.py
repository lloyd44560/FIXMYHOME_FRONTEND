from django.db import models
import uuid
from django.conf import settings

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
