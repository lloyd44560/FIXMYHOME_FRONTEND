from django.db import models

class TraderRegistration(models.Model):
    # Auth Details of the trader
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    
    # Company Details
    company_type = models.CharField(max_length=100)
    company_name = models.CharField(max_length=255, blank=True)
    company_address = models.CharField(max_length=255, blank=True)
    company_email = models.EmailField(blank=True)
    company_landline = models.CharField(max_length=50, blank=True)
    contractor_license = models.CharField(max_length=100, blank=True)
    gst_registered = models.BooleanField(default=False)
    abn = models.CharField(max_length=20, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    other_expertise = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
