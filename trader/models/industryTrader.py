from django.db import models
from .registerTrader import TraderRegistration 

class TraderIndustry(models.Model):
    INDUSTRIES_CHOICES = [
        ('air_conditioning', 'Air Conditioning'),
        ('cleaning', 'Cleaning'),
        ('electrical', 'Electrical'),
        ('gardening', 'Gardening'),
        ('general_maintenance', 'General Maintenance'),
        ('glazing', 'Glazing'),
        ('pest_control', 'Pest Control'),
        ('plumbing_gas', 'Plumbing / Gas'),
        ('tree_cutting', 'Tree Cutting'),
        ('steel_works', 'Steel Works'),
        ('safety', 'Safety'),
    ]

    trader = models.ForeignKey(TraderRegistration, on_delete=models.CASCADE, related_name='industries')
    industry = models.CharField(max_length=100, choices=INDUSTRIES_CHOICES)

    def __str__(self):
        return f"{self.get_industry_display()} ({self.trader.name})"