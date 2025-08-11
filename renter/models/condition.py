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



class MainConditionReport(models.Model):
    report_number = models.CharField(max_length=100, unique=True)  # e.g. CR-0001
    date_created = models.DateField(auto_now_add=True)
    renter = models.ForeignKey(Renter, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='condition_reports/', null=True, blank=True)

    def __str__(self):
        return self.report_number



class ConditionReportRoom(models.Model):
    report = models.ForeignKey(MainConditionReport, on_delete=models.CASCADE, related_name='report_rooms')
    room = models.ForeignKey('renter.RenterRoom', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.report.report_number} - {self.room.room_name}"



class RenterRoom(models.Model):
    renter = models.ForeignKey(Renter, on_delete=models.CASCADE,null=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE,null=True)
    room_name = models.CharField(max_length=255,null=True)
    description = models.TextField(blank=True,null=True)
    photo = models.ImageField(upload_to='room_photos/', blank=True, null=True)

    def __str__(self):
        return self.room_name

class RenterRoomAreaCondition(models.Model):
    room = models.ForeignKey('RenterRoom', on_delete=models.CASCADE, related_name='area_conditions')
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

    # ✅ Optional: Photo
    photo = models.ImageField(upload_to='area_condition_photos/', blank=True, null=True)

    # ✅ Optional: Remarks field
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.area_name} - {self.status}"



class Room(models.Model):
    name = models.CharField(max_length=255)



class RoomConditionReport(models.Model):
    renter = models.ForeignKey('renter.Renter', on_delete=models.CASCADE, related_name='room_condition_reports')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.room_name} (Report #{self.id})"


class RoomConditionAreaReport(models.Model):
    report = models.ForeignKey(RoomConditionReport, on_delete=models.CASCADE, related_name='area_reports')
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
        return f"{self.area_name} - {self.status}"


class RoomApplianceReport(models.Model):
    renter = models.ForeignKey('renter.Renter', on_delete=models.CASCADE)
    room = models.ForeignKey('renter.RenterRoom', on_delete=models.CASCADE, related_name='appliances')
    window_height = models.CharField(max_length=50, blank=True)
    window_length = models.CharField(max_length=50, blank=True)
    window_width = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model_serial = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='appliance_photos/', blank=True, null=True)
    comments = models.TextField(blank=True)
    appliance_photo = models.ImageField(upload_to='appliances/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 5 appliance photo fields
    photo1 = models.ImageField(upload_to='appliance_photos/', blank=True, null=True)
    photo2 = models.ImageField(upload_to='appliance_photos/', blank=True, null=True)
    photo3 = models.ImageField(upload_to='appliance_photos/', blank=True, null=True)
    photo4 = models.ImageField(upload_to='appliance_photos/', blank=True, null=True)
    photo5 = models.ImageField(upload_to='appliance_photos/', blank=True, null=True)
