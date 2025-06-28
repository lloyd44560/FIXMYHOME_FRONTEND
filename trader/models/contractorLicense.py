from django.db import models
from .registerTrader import TraderRegistration 

class ContractorLicense(models.Model):
    trader = models.ForeignKey(TraderRegistration, 
        on_delete=models.CASCADE, related_name='contractor_license')
    contractorLicense = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.contractorLicense} ({self.id})"