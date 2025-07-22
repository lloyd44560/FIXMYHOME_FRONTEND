from django.db import models

class Services(models.Model):
    keyword = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    isurgent = models.BooleanField(default=False, help_text="Is this service urgent?")
    locationName = models.CharField(max_length=100, blank=True, null=True)
    marketName = models.CharField(max_length=100, blank=True, null=True)
    secondaryMarketName = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Is this service currently active?")

    def __str__(self):
        return self.keyword