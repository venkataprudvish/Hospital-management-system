from django.conf import settings
from django.db import models
from django.db.models import Q


class Profile(models.Model):
    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_DOCTOR = "doctor"
    ROLE_NURSE = "nurse"
    ROLE_RECEPTIONIST = "receptionist"
    ROLE_ACCOUNTANT = "accountant"
    ROLE_PATIENT = "patient"

    ROLE_CHOICES = [
        (ROLE_OWNER, "Hospital Owner"),
        (ROLE_ADMIN, "Administrator"),
        (ROLE_DOCTOR, "Doctor"),
        (ROLE_NURSE, "Nurse / Staff"),
        (ROLE_RECEPTIONIST, "Receptionist"),
        (ROLE_ACCOUNTANT, "Accountant"),
        (ROLE_PATIENT, "Patient"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_PATIENT,
        db_index=True,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(
                    role__in=[
                        "owner",
                        "admin",
                        "doctor",
                        "nurse",
                        "receptionist",
                        "accountant",
                        "patient",
                    ]
                ),
                name="profile_valid_role",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} "
            f"({self.get_role_display()})"
        )