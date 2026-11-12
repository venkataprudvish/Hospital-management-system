from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("authentication", "0001_initial")]
    operations = [
        migrations.CreateModel(name="Doctor", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("first_name", models.CharField(max_length=80)), ("last_name", models.CharField(max_length=80)),
            ("specialization", models.CharField(max_length=120)), ("license_number", models.CharField(blank=True, max_length=80)),
            ("contact_number", models.CharField(blank=True, max_length=30)), ("room", models.CharField(blank=True, max_length=30)),
            ("is_available", models.BooleanField(default=True)), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("user", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="doctor_record", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering":["first_name","last_name"]}),
        migrations.CreateModel(name="Patient", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("first_name", models.CharField(max_length=80)), ("last_name", models.CharField(max_length=80)),
            ("date_of_birth", models.DateField(blank=True, null=True)), ("gender", models.CharField(blank=True, max_length=30)),
            ("contact_number", models.CharField(blank=True, max_length=30)), ("address", models.TextField(blank=True)),
            ("emergency_contact", models.CharField(blank=True, max_length=120)), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("user", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="patient_record", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering":["first_name","last_name"]}),
    ]
