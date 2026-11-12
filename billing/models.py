from django.conf import settings
from django.db import models
from django.db.models import Q

from records.models import Patient
from appointments.models import Appointment


class Bill(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="bills",
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.PROTECT,
        related_name="bills",
        null=True,
        blank=True,
    )

    description = models.CharField(
        max_length=200,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_bills",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gte=0),
                name="bill_amount_non_negative",
            ),
        ]

        indexes = [
            models.Index(
                fields=["patient", "status"],
                name="bill_patient_status_idx",
            ),
            models.Index(
                fields=["status", "created_at"],
                name="bill_status_created_idx",
            ),
        ]

    def __str__(self):
        return (
            f"Invoice #{self.pk} — "
            f"{self.patient} — ₹{self.amount}"
        )