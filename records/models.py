from django.conf import settings
from django.db import models


class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="patient_record",
        null=True,
        blank=True,
    )

    first_name = models.CharField(
        max_length=80,
    )

    last_name = models.CharField(
        max_length=80,
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    gender = models.CharField(
        max_length=30,
        blank=True,
    )

    contact_number = models.CharField(
        max_length=30,
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    emergency_contact = models.CharField(
        max_length=120,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "first_name",
            "last_name",
        ]

        indexes = [
            models.Index(
                fields=["last_name", "first_name"],
                name="patient_name_idx",
            ),
            models.Index(
                fields=["contact_number"],
                name="patient_contact_idx",
            ),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="doctor_record",
        null=True,
        blank=True,
    )

    first_name = models.CharField(
        max_length=80,
    )

    last_name = models.CharField(
        max_length=80,
    )

    specialization = models.CharField(
        max_length=120,
    )

    license_number = models.CharField(
        max_length=80,
        blank=True,
    )

    contact_number = models.CharField(
        max_length=30,
        blank=True,
    )

    room = models.CharField(
        max_length=30,
        blank=True,
    )

    is_available = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "first_name",
            "last_name",
        ]

        indexes = [
            models.Index(
                fields=["last_name", "first_name"],
                name="doctor_name_idx",
            ),
            models.Index(
                fields=["is_available"],
                name="doctor_available_idx",
            ),
            models.Index(
                fields=["specialization"],
                name="doctor_specialization_idx",
            ),
        ]

    def __str__(self):
        return (
            f"Dr. {self.first_name} "
            f"{self.last_name} — "
            f"{self.specialization}"
        )