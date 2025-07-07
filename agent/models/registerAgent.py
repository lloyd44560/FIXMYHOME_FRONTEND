from django.db import models
from django.urls import reverse

from django.contrib.auth.models import User

class AgentRegister(models.Model):
    # User Authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    # Trader Details
    SERVICE_CHOICES = [
        ('air_conditioning', 'Air Conditioning'),
        ('cleaning', 'Cleaning'),
        ('electrical', 'Electrical'),
        ('gardening', 'Gardening'),
        ('general_merchandise', 'General Merchandise'),
        ('glazing', 'Glazing'),
        ('pest_control', 'Pest Control'),
        ('plumbing-gas', 'Plumbing / Gas'),
        ('tree_cutting', 'Tree Cutting'),
        ('steel_works', 'Steel Works'),
    ]
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=50)
    agency_id = models.CharField(max_length=50)
    website = models.CharField(max_length=50)
    notes = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True)

    # Company Details
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_address = models.CharField(max_length=255, blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)
    company_landline = models.CharField(max_length=50, blank=True, null=True)
    contractor_license = models.CharField(max_length=100, blank=True)
    service = models.CharField(max_length=100, choices=SERVICE_CHOICES, blank=True, null=True)

    # Rates
    state = models.CharField(max_length=100, blank=True)
    municipality = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('agent:register_agent', args=[str(self.id)])