from django.db import models
from django.urls import reverse

from django.contrib.auth.models import User
from renter.models import Renter
from .propertyAgent import Property

class Rooms(models.Model):
    renter = models.ForeignKey(Renter, on_delete=models.SET_NULL, related_name='renter_rooms', null=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_rooms')

    room_name = models.CharField(max_length=100)
    room_photo = models.ImageField(upload_to='rooms/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.room_name