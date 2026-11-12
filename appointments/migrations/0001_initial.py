from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("records", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="Appointment", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("date_time", models.DateTimeField()), ("reason", models.CharField(max_length=300)),
        ("status", models.CharField(choices=[("scheduled", "Scheduled"), ("confirmed", "Confirmed"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="scheduled", max_length=20)),
        ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
        ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_appointments", to=settings.AUTH_USER_MODEL)),
        ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointments", to="records.doctor")),
        ("patient", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointments", to="records.patient")),
    ], options={"ordering":["date_time"]}), migrations.AddIndex(model_name="appointment", index=models.Index(fields=["doctor","date_time"], name="appointments_doctor_5a3b8a_idx")), migrations.AddIndex(model_name="appointment", index=models.Index(fields=["patient","date_time"], name="appointments_patient_6bbfe7_idx"))]
