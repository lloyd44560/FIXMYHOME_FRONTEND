from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Renter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    # Step 1 - Personal Info
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=128)  # store hashed password (later)

    # Step 2 - Company Info (some fields optional)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_person_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    company_address_line1 = models.CharField(max_length=255, blank=True, null=True)
    company_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    company_postal_code = models.CharField(max_length=20, blank=True, null=True)

    # Step 3 - Upload Option and Property Details
    upload_option = models.CharField(max_length=50, blank=True, null=True)  # 'manual' or 'report'

    # Property manual upload fields
    property_image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    floor_count = models.PositiveIntegerField(blank=True, null=True)
    room_count = models.PositiveIntegerField(blank=True, null=True)

    # You can store rooms as JSON or in another related model
    rooms = models.JSONField(blank=True, null=True)  # example: [{"type": "Bedroom"}, {"type": "Kitchen"}]

    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    house_state = models.CharField(max_length=100, blank=True, null=True)
    house_city = models.CharField(max_length=100, blank=True, null=True)
    house_zip = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name