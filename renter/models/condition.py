from django.db import models
from agent.models.propertyAgent import Property
from renter.models import Renter


class ConditionReport(models.Model):
    renter = models.OneToOneField('renter.Renter', on_delete=models.CASCADE)
    data = models.JSONField()

    def __str__(self):
        return f"Condition Report for {self.renter}"

class RoomCondition(models.Model):
    property = models.ForeignKey('renter.Property', on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255)
    width = models.CharField(max_length=50, blank=True, null=True)
    length = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='rooms/', null=True, blank=True)

    # Additional fields
    condition_report_date = models.CharField(max_length=100, blank=True)
    agreement_start_date = models.CharField(max_length=100, blank=True)
    renter_received_date = models.CharField(max_length=100, blank=True)
    report_return_date = models.CharField(max_length=100, blank=True)

    address = models.TextField(blank=True)
    full_name_1 = models.CharField(max_length=100, blank=True)
    agent_name = models.CharField(max_length=100, blank=True)
    agent_company_name = models.CharField(max_length=100, blank=True)
    renter_1 = models.CharField(max_length=100, blank=True)
    renter_2 = models.CharField(max_length=100, blank=True)


class RenterRoom(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    renter = models.ForeignKey('Renter', on_delete=models.CASCADE, related_name='renter_room_items')  # <-- changed
    def __str__(self):
        return self.room_name

class RenterRoomAreaCondition(models.Model):
    room = models.ForeignKey(RenterRoom, on_delete=models.CASCADE, related_name='area_conditions')
    area_name = models.CharField(max_length=255)

    status = models.CharField(
        max_length=100,
        choices=[
            ('Clean', 'Clean'),
            ('Undamaged', 'Undamaged'),
            ('Working', 'Working'),
        ],
        default='Clean'
    )

    def __str__(self):
        return f"{self.area_name} ({self.status})"



class Room(models.Model):
    name = models.CharField(max_length=255)