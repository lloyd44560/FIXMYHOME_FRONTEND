from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from django.conf import settings

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
    gender = models.CharField(max_length=10, null=True, blank=True)
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

class FailedLoginAttempt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    locked_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.attempts} attempts"

class ConditionReport(models.Model):
    renter = models.OneToOneField('Renter', on_delete=models.CASCADE)  # One condition report per renter
    data = models.JSONField()  # You can store the entire modal form data as JSON

    def __str__(self):
        return f"Condition Report for {self.renter.name}"

class EmailVerification(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token      = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} — {self.token}"

# create model for Properties
class Property(models.Model):
    renter = models.ForeignKey('Renter', on_delete=models.SET_NULL, related_name='properties', null=True, blank=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='assigned_properties')
    property_name = models.CharField(max_length=255)
    floor_count = models.PositiveIntegerField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    property_photo = models.ImageField(upload_to='property_photos/', blank=True, null=True)
    condition_report = models.ImageField(upload_to='condition_reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.property_name} ({self.city}, {self.state})'

# # Create a rooms Model
# class Room(models.Model):
#     property = models.ForeignKey(Property, on_delete=models.CASCADE)
#     room_name = models.CharField(max_length=100)
#     description = models.TextField(blank=True, null=True)
#     renter = models.ForeignKey('Renter', on_delete=models.CASCADE, related_name='room_items', null=True)

#     def __str__(self):
#         return self.room_name