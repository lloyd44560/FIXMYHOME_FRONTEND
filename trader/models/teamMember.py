from django.db import models
from .registerTrader import TraderRegistration 

class TeamMember(models.Model):
    trader = models.ForeignKey(TraderRegistration, 
        on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=100)
    labour_rate_per_hour = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    callout_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    active_postal_codes = models.CharField(max_length=255, blank=True)  # Comma-separated
    holidays = models.TextField(blank=True)  # Store as comma-separated dates or JSON
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)

    # For Sole Trader
    IsWorkInHoliday = models.BooleanField(default=False)
    holidayTime_in = models.TimeField(null=True, blank=True)
    holidayTime_out = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.id})"