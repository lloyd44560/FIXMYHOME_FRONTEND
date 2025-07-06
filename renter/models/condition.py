from django.db import models    

class ConditionReport(models.Model):
    renter = models.OneToOneField('renter.Renter', on_delete=models.CASCADE)
    data = models.JSONField()

    def __str__(self):
        return f"Condition Report for {self.renter}"

class RoomCondition(models.Model):
    property = models.ForeignKey('renter.Property', on_delete=models.CASCADE)
    renter = models.ForeignKey('renter.Renter', on_delete=models.CASCADE)
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

class RoomAreaCondition(models.Model):
    room_condition = models.ForeignKey(RoomCondition, related_name='areas', on_delete=models.CASCADE)
    area_name = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    renter_comment = models.TextField(blank=True)  
