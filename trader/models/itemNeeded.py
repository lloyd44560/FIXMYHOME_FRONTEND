from django.db import models

class ItemNeeded(models.Model):
    bidding = models.ForeignKey('Bidding', 
        on_delete=models.CASCADE, 
        related_name='items_needed', 
        null=True, blank=True
    )
    name = models.CharField(max_length=100)
    price = models.FloatField(null=True, blank=True, default=0)

    def __str__(self):
        return f"{self.name} - {self.price or 0:.2f}"