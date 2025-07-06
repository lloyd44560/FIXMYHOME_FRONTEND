from django.db import models

class Room(models.Model):
    property = models.ForeignKey('renter.Property', on_delete=models.CASCADE, related_name='rooms')
    room_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    renter = models.ForeignKey('renter.Renter', on_delete=models.CASCADE, related_name='room_items', null=True)

    def __str__(self):
        return self.room_name
