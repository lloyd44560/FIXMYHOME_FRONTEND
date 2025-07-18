from django.db import models
from agent.models.propertyAgent import Property

class Room(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,  # Avoid crashes if Property is deleted
        null=True,
        blank=True
    )
    room_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    renter = models.ForeignKey(
        'Renter',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='simple_room_items'
    )

    def __str__(self):
        return self.room_name