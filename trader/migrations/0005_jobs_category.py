# Generated by Django 5.2.1 on 2025-07-22 20:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0004_services_alter_traderregistration_industry_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category_services', to='trader.services'),
        ),
    ]
