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
    bid_status = models.CharField(max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')
    bid_count = models.IntegerField(default=0)
    quoted_at = models.DateField(default=timezone.now)
    confirmed_at = models.DateField(null=True, blank=True)
    approved_at = models.DateField(null=True, blank=True)
    scheduled_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True, default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Added for backlogs Creation of Maintenance Request by Renter: Add selections for "When did the issue occur?" and
    issue_found_at = models.DateField(null=True, blank=True)
    renter_availability = models.DateField(null=True, blank=True)
    issue_been_fixed_before = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Always regenerate job_code based on current status
        # prefix = self.status[:3].upper()  # 'QUO', 'APP', etc.

        # --- Auto close bid if bid_count >= 3 ---
        if self.bid_count >= 3:
            self.bid_status = "closed"
        else:
            self.bid_status = "open"

        # --- Generate job_code only if not set (to avoid regenerating on every save) ---
        if not self.job_code:
            count = 1
            base_code = f"JOB{count:05d}"

            # Increment until unique
            while Jobs.objects.filter(job_code=base_code).exists():
                count += 1
                base_code = f"JOB{count:05d}"

            self.job_code = base_code
        super().save(*args, **kwargs)

    def __str__(self):
        return self.job_code





# Added for multiple images for maintenance requests
class JobImage(models.Model):
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="job_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.job.job_code}"
