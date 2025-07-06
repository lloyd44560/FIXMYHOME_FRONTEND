from django.db import models

class Property(models.Model):
    renter = models.ForeignKey('renter.Renter', on_delete=models.SET_NULL, related_name='properties', null=True, blank=True)
    # agent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='assigned_properties')
    property_name = models.CharField(max_length=255)
    floor_count = models.PositiveIntegerField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    property_photo = models.ImageField(upload_to='property_photos/', blank=True, null=True)
    condition_report = models.ImageField(upload_to='condition_reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.property_name} ({self.city}, {self.state})'
