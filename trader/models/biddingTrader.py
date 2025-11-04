from django.db import models
from django.utils import timezone

from agent.models import AgentRegister
from .registerTrader import TraderRegistration
from .jobs import Jobs
from .teamMember import TeamMember
from .itemNeeded import ItemNeeded

class Bidding(models.Model):
    trader = models.ForeignKey(TraderRegistration, on_delete=models.CASCADE, related_name='bid_trader')
    agent = models.ForeignKey(AgentRegister, on_delete=models.SET_NULL, null=True, blank=True, related_name='bid_agent')
    jobs = models.ForeignKey(Jobs, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs_related')

    # 👇 Link to your detailed TeamMember
    team_member = models.ManyToManyField(TeamMember, related_name='biddings_related', blank=True)

    # Auto-generated code for the bid
    quote_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    
    # Rates can be auto-filled from the team member
    labour_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    callout_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    parts_qty = models.PositiveIntegerField(default=0)
    parts_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    appliance_model_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    appliance_model = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    # Approval fields
    is_approved = models.BooleanField(null=True, blank=True, default=None, help_text="None=pending, True=approved, False=rejected")
    is_active = models.BooleanField(null=True, blank=True, default=True)
    approved_at = models.DateField(auto_now_add=True, null=True, blank=True)
    approved_by = models.ForeignKey(AgentRegister, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bids')
    approval_notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.quote_code:
            last_bid = Bidding.objects.order_by('-id').first()
            next_number = 1
            if last_bid and last_bid.quote_code and last_bid.quote_code[3:].isdigit():
                next_number = int(last_bid.quote_code[3:]) + 1
            self.quote_code = f"QUO{next_number:05d}"
        super().save(*args, **kwargs)
    
    def subtotal(self):
        return (
            (self.labour_per_hour or 0) * (self.hours or 0)
            + (self.callout_rate or 0)
            + (self.parts_qty * self.parts_unit_price)
            + self.appliance_model_price
        )

    def gst(self):
        return self.subtotal() * 0.10

    def total(self):
        return self.subtotal() + self.gst()

    def __str__(self):
        return self.code




