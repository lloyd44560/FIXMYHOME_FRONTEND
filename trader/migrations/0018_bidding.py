# Generated by Django 5.2.1 on 2025-07-02 13:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0005_alter_property_agent'),
        ('trader', '0017_jobs_priority'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bidding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('labour_per_hour', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('callout_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('parts_qty', models.PositiveIntegerField(default=0)),
                ('parts_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('hours', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('appliance_model_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('appliance_model', models.CharField(blank=True, max_length=100, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bid_agent', to='agent.agentregister')),
                ('jobs', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='jobs_related', to='trader.jobs')),
                ('team_member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teams_related', to='trader.teammember')),
                ('trader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bid_trader', to='trader.traderregistration')),
            ],
        ),
    ]
