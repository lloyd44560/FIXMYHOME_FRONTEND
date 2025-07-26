from django.db import models
from django.utils import timezone

from agent.models import AgentRegister, Property
from .registerTrader import TraderRegistration
from .servicesTrader import Services

class Jobs(models.Model):
    agent = models.ForeignKey(AgentRegister, on_delete=models.CASCADE, related_name='jobs_agent')
    trader = models.ForeignKey(TraderRegistration, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs_trader')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs_property')
    
    STATUS_CHOICES = [
        ('quoted', 'Quoted'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled'),
    ]
    address = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Services, on_delete=models.SET_NULL, null=True, blank=True, related_name='category_services')
    renter = models.CharField(max_length=100, null=True, blank=True)
    priority = models.BooleanField(default=False)  # True = High Priority
    job_code = models.CharField(max_length=20, unique=True)
    notes = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='quoted')
    quoted_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Always regenerate job_code based on current status
        prefix = self.status[:3].upper()  # 'QUO', 'APP', etc.
        
        count = 1
        base_code = f"{prefix}-{count:05d}"

        # Increment until unique
        while Jobs.objects.exclude(pk=self.pk).filter(job_code=base_code).exists():
            count += 1
            base_code = f"{prefix}-{count:05d}"

        self.job_code = base_code

        super().save(*args, **kwargs)

    def __str__(self):
        return self.job_code