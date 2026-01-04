from django.db import models, IntegrityError, transaction
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
    issue_been_fixed_by_fmh_before = models.BooleanField(default=False)
    renter_availability_schedule = models.JSONField(null=True, blank=True, default=dict)
    renter_issue_date = models.JSONField(blank=True, null=True, default=dict)


    def save(self, *args, **kwargs):
        # Auto-close bid if bid_count >= 3
        self.bid_status = "closed" if self.bid_count >= 3 else "open"

        # Generate job_code if not set
        if not self.job_code:
            for _ in range(5):  # try 5 times to avoid race condition
                last_job = Jobs.objects.order_by('-id').first()
                next_number = 1
                if last_job and last_job.job_code and last_job.job_code[3:].isdigit():
                    next_number = int(last_job.job_code[3:]) + 1
                self.job_code = f"JOB{next_number:05d}"

                try:
                    with transaction.atomic():
                        super().save(*args, **kwargs)
                    break  # success
                except IntegrityError:
                    self.job_code = None  # retry with next number
        else:
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
