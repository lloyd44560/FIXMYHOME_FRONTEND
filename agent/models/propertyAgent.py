import re
from django.db import models, transaction, IntegrityError
from django.urls import reverse

from django.contrib.auth.models import User
from renter.models import Renter
from .registerAgent import AgentRegister

def street_code(street: str | None) -> str:
    """Take first 4 letters from street (letters only), uppercase, pad with X."""
    if not street:
        return "XXXX"
    letters_only = re.sub(r'[^A-Za-z]', '', street).upper()
    return (letters_only + "XXXX")[:4]

class Property(models.Model):
    renter = models.ForeignKey(Renter, on_delete=models.SET_NULL, related_name='rent_property', null=True, blank=True)
    agent = models.ForeignKey(AgentRegister, on_delete=models.CASCADE, null=False, related_name='own_properties')

    property_id = models.CharField(max_length=100, blank=True, null=True)
    ref_number = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    floor_count = models.PositiveIntegerField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=True)
    house_number = models.CharField(max_length=20, blank=True, null=True)
    renter_name = models.CharField(max_length=100, blank=True, null=True)
    renter_contact = models.CharField(max_length=20, blank=True, null=True)
    key_number = models.CharField(max_length=20, blank=True, null=True)
    rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    property_photo = models.ImageField(upload_to='property_photos/', blank=True, null=True)
    condition_report = models.ImageField(upload_to='condition_reports/', blank=True, null=True)
    lease_start = models.DateField()
    lease_end = models.DateField()
    is_active = models.BooleanField(null=True, blank=True, default=True)
    
    STATUS_CHOICES = [
        ('occupied', 'Occupied'),
        ('vacant', 'Vacant'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='vacant')

    def _next_ref_number(self) -> str:
        prefix = street_code(self.street)

        # Lock matching rows to avoid duplicate numbers under concurrency
        with transaction.atomic():
            last = (Property.objects
                    .select_for_update()
                    .filter(ref_number__startswith=prefix)
                    .order_by('-ref_number')
                    .values_list('ref_number', flat=True)
                    .first())
            last_seq = int(last[-5:]) if last and last[-5:].isdigit() else 0
            return f"{prefix}{last_seq + 1:05d}"

    def save(self, *args, **kwargs):
        if not self.ref_number:
            # Retry a few times in case of race (unique constraint collision)
            for _ in range(5):
                self.ref_number = self._next_ref_number()
                try:
                    return super().save(*args, **kwargs)
                except IntegrityError:
                    # Someone took that number at the same time—try again
                    continue
            # If still failing, bubble up the last error
            # (realistically shouldn't happen beyond extreme contention)
            return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.ref_number}'