from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("appointments", "0001_initial"), ("records", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="Bill", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("description", models.CharField(max_length=200)), ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
        ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid"), ("cancelled", "Cancelled")], default="pending", max_length=20)),
        ("created_at", models.DateTimeField(auto_now_add=True)), ("paid_at", models.DateTimeField(blank=True, null=True)),
        ("appointment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="bills", to="appointments.appointment")),
        ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
        ("patient", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bills", to="records.patient")),
    ], options={"ordering":["-created_at"]})]
