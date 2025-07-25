# Generated by Django 4.2.11 on 2025-07-19 01:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("agent", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Property",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("property_name", models.CharField(max_length=255)),
                ("floor_count", models.PositiveIntegerField()),
                ("state", models.CharField(max_length=100)),
                ("city", models.CharField(max_length=100)),
                ("address_line1", models.CharField(max_length=255)),
                (
                    "address_line2",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("postal_code", models.CharField(max_length=20)),
                (
                    "property_photo",
                    models.ImageField(
                        blank=True, null=True, upload_to="property_photos/"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "condition_report",
                    models.FileField(
                        blank=True, null=True, upload_to="condition_reports/"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Renter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("phone", models.CharField(max_length=20)),
                ("password", models.CharField(max_length=128)),
                ("gender", models.CharField(blank=True, max_length=10, null=True)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "company_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "contact_person",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "contact_person_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                (
                    "contact_phone",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("state", models.CharField(blank=True, max_length=100, null=True)),
                ("city", models.CharField(blank=True, max_length=100, null=True)),
                ("zip_code", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "company_address_line1",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "company_address_line2",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "company_postal_code",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "upload_option",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "property_image",
                    models.ImageField(
                        blank=True, null=True, upload_to="property_images/"
                    ),
                ),
                ("floor_count", models.PositiveIntegerField(blank=True, null=True)),
                ("room_count", models.PositiveIntegerField(blank=True, null=True)),
                ("rooms", models.JSONField(blank=True, null=True)),
                (
                    "address_line1",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "address_line2",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "house_state",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("house_city", models.CharField(blank=True, max_length=100, null=True)),
                ("house_zip", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RenterRoom",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("room_name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="agent.property"
                    ),
                ),
                (
                    "renter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="renter_room_items",
                        to="renter.renter",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="RoomConditionReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("room_name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="agent.property"
                    ),
                ),
                (
                    "renter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="room_condition_reports",
                        to="renter.renter",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RoomConditionAreaReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("area_name", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Clean", "Clean"),
                            ("Undamaged", "Undamaged"),
                            ("Working", "Working"),
                        ],
                        default="Clean",
                        max_length=100,
                    ),
                ),
                (
                    "report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="area_reports",
                        to="renter.roomconditionreport",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RoomCondition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("room_name", models.CharField(max_length=255)),
                ("width", models.CharField(blank=True, max_length=50, null=True)),
                ("length", models.CharField(blank=True, max_length=50, null=True)),
                ("photo", models.ImageField(blank=True, null=True, upload_to="rooms/")),
                ("condition_report_date", models.CharField(blank=True, max_length=100)),
                ("agreement_start_date", models.CharField(blank=True, max_length=100)),
                ("renter_received_date", models.CharField(blank=True, max_length=100)),
                ("report_return_date", models.CharField(blank=True, max_length=100)),
                ("address", models.TextField(blank=True)),
                ("full_name_1", models.CharField(blank=True, max_length=100)),
                ("agent_name", models.CharField(blank=True, max_length=100)),
                ("agent_company_name", models.CharField(blank=True, max_length=100)),
                ("renter_1", models.CharField(blank=True, max_length=100)),
                ("renter_2", models.CharField(blank=True, max_length=100)),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="renter.property",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RenterRoomAreaCondition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("area_name", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Clean", "Clean"),
                            ("Undamaged", "Undamaged"),
                            ("Working", "Working"),
                        ],
                        default="Clean",
                        max_length=100,
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="area_conditions",
                        to="renter.renterroom",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="property",
            name="renter",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="properties",
                to="renter.renter",
            ),
        ),
        migrations.CreateModel(
            name="MinimumStandardReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tenant_name", models.CharField(max_length=255)),
                ("audit_no", models.CharField(max_length=100)),
                ("auditor", models.CharField(max_length=255)),
                ("inspection_address", models.TextField()),
                ("managing_agent", models.CharField(max_length=255)),
                ("audit_date", models.DateField()),
                ("room", models.CharField(max_length=255)),
                ("comments", models.TextField(blank=True, null=True)),
                (
                    "report_file",
                    models.FileField(
                        blank=True, null=True, upload_to="standard_reports/"
                    ),
                ),
                (
                    "renter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="renter.renter"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FailedLoginAttempt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("attempts", models.IntegerField(default=0)),
                ("is_locked", models.BooleanField(default=False)),
                ("locked_until", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EmailVerification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "token",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ConditionReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data", models.JSONField()),
                (
                    "renter",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="renter.renter"
                    ),
                ),
            ],
        ),
    ]
