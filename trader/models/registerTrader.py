from django.db import models
from django.urls import reverse

from django.contrib.auth.models import User

class TraderRegistration(models.Model):
    # User Authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    # Trader Details
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    password = models.CharField(max_length=255, null=True, blank=True)

    # Trader Roles
    isAdmin = models.BooleanField(default=False)
    isDirector = models.BooleanField(default=True)
    isTeamMember = models.BooleanField(default=False)
    
    # Company Details
    COMPANY_TYPE_CHOICES = [
        ('sole_trader', 'Sole Trader'),
        ('company', 'Company'),
    ]
    INDUSTRIES_CHOICES = [
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

    company_type = models.CharField(max_length=100, choices=COMPANY_TYPE_CHOICES, default='company')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_address = models.CharField(max_length=255, blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)
    company_landline = models.CharField(max_length=50, blank=True, null=True)
    gst_registered = models.BooleanField(default=False)
    abn = models.CharField(max_length=20, blank=True, null=True)
    industry = models.CharField(max_length=100, choices=INDUSTRIES_CHOICES, blank=True, null=True)

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
        return reverse('trader:register_submit', args=[str(self.id)])