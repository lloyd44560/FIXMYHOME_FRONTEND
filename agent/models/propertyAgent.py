from django.db import models
from django.urls import reverse

from django.contrib.auth.models import User
from renter.models import Renter
from .registerAgent import AgentRegister

class Property(models.Model):
    renter = models.ForeignKey(Renter, on_delete=models.SET_NULL, related_name='rent_property', null=True, blank=True)
    agent = models.ForeignKey(AgentRegister, on_delete=models.CASCADE, null=False, related_name='own_properties')

    name = models.CharField(max_length=100, blank=True, null=True)
    floor_count = models.PositiveIntegerField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    renter_name = models.CharField(max_length=100, blank=True, null=True)
    renter_contact = models.CharField(max_length=20, blank=True, null=True)
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

    def __str__(self):
        return f'{self.name} ({self.city}, {self.state})'