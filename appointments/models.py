from django.conf import settings
from django.db import models
from django.db.models import Q

from records.models import Patient, Doctor


class Appointment(models.Model):
    STATUS_SCHEDULED = "scheduled"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    date_time = models.DateTimeField()

    reason = models.CharField(
        max_length=300,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_appointments",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["date_time"]

        indexes = [
            models.Index(
                fields=["doctor", "date_time"],
                name="appt_doctor_datetime_idx",
            ),
            models.Index(
                fields=["patient", "date_time"],
                name="appt_patient_datetime_idx",
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "date_time"],
                condition=Q(
                    status__in=[
                        "scheduled",
                        "confirmed",
                        "completed",
                    ]
                ),
                name="unique_active_doctor_datetime",
            ),
        ]

    def __str__(self):
        return (
            f"{self.patient} with {self.doctor} "
            f"at {self.date_time:%Y-%m-%d %H:%M}"
        )