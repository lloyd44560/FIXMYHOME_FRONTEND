from django.db import models

class ApplianceReport(models.Model):
    room = models.ForeignKey('renter.Room', on_delete=models.CASCADE, related_name='appliance_reports')
    renter = models.ForeignKey('renter.Renter', on_delete=models.CASCADE)

    window_height = models.CharField(max_length=50, blank=True)
    window_length = models.CharField(max_length=50, blank=True)
    window_width = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model_serial = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='appliance_photos/', blank=True, null=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    appliance_photo = models.ImageField(upload_to='appliances/', null=True, blank=True)


    def __str__(self):
        return f"{self.room.room_name} Report by {self.renter.user.username}"
