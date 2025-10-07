from django.db import models
from django.utils import timezone

from trader.models import TraderRegistration, TeamMember
from agent.models import AgentRegister

class Leaves(models.Model):
    trader = models.ForeignKey(TraderRegistration, on_delete=models.CASCADE, related_name='leave_trader')

    LEAVE_TYPE_CHOICES = [
        ('vacation', 'Vacation Leave'),
        ('sick', 'Sick Leave'),
    ]
    
    ref_number = models.CharField(max_length=20, unique=True)
    team_member = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='leave_teams_related')
    leave_type = models.CharField(max_length=100, choices=LEAVE_TYPE_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(null=True, blank=True, default=True)

    # Approval fields
    status = models.CharField(max_length=50, default="Pending")  # Pending / Approved / Rejected
    is_approved = models.BooleanField(null=True, blank=True, default=None, help_text="None=pending, True=approved, False=rejected")
    approved_at = models.DateField(auto_now_add=True, null=True, blank=True)
    approved_by = models.ForeignKey(AgentRegister, on_delete=models.SET_NULL, null=True, blank=True, related_name='leave_approve_by')
    approval_notes = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Always regenerate ref_number
        count = 1
        base_code = f"HOL-{count:05d}"

        # Increment until unique
        while Leaves.objects.exclude(pk=self.pk).filter(ref_number=base_code).exists():
            count += 1
            base_code = f"HOL-{count:05d}"

        self.ref_number = base_code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.leave_type} ({self.team_member.name})"
