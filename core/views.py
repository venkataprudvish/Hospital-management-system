from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from authentication.models import Profile
from appointments.models import Appointment
from billing.models import Bill
from records.models import Doctor, Patient
from core.utils import has_role


DASHBOARD_STAFF_ROLES = (
    Profile.ROLE_OWNER,
    Profile.ROLE_ADMIN,
    Profile.ROLE_NURSE,
    Profile.ROLE_RECEPTIONIST,
)


@login_required
def dashboard(request):
    """
    Render the dashboard with statistics appropriate to the
    authenticated user's role.

    The dashboard exposes aggregate information only.
    Individual patient, doctor, appointment, and billing
    records are not placed into the dashboard context.
    """

    profile = getattr(
        request.user,
        "profile",
        None,
    )

    context = {
        "profile": profile,
    }

    # ---------------------------------------------------------
    # Hospital staff / administrators
    # ---------------------------------------------------------

    if (
        request.user.is_superuser
        or has_role(
            request.user,
            *DASHBOARD_STAFF_ROLES,
        )
    ):
        context.update(
            {
                "patient_count": Patient.objects.count(),

                "doctor_count": Doctor.objects.count(),

                "appointment_count": Appointment.objects.count(),

                "pending_bills": (
                    Bill.objects
                    .filter(
                        status=Bill.STATUS_PENDING,
                    )
                    .count()
                ),
            }
        )

        return render(
            request,
            "core/dashboard.html",
            context,
        )

    # ---------------------------------------------------------
    # Doctor
    # ---------------------------------------------------------

    doctor_record = getattr(
        request.user,
        "doctor_record",
        None,
    )

    if doctor_record is not None:
        context["appointment_count"] = (
            Appointment.objects
            .filter(
                doctor=doctor_record,
            )
            .count()
        )

        return render(
            request,
            "core/dashboard.html",
            context,
        )

    # ---------------------------------------------------------
    # Patient
    # ---------------------------------------------------------

    patient_record = getattr(
        request.user,
        "patient_record",
        None,
    )

    if patient_record is not None:
        context["appointment_count"] = (
            Appointment.objects
            .filter(
                patient=patient_record,
            )
            .count()
        )

        context["pending_bills"] = (
            Bill.objects
            .filter(
                patient=patient_record,
                status=Bill.STATUS_PENDING,
            )
            .count()
        )

        return render(
            request,
            "core/dashboard.html",
            context,
        )

    # ---------------------------------------------------------
    # Authenticated user without a recognized record/role
    # ---------------------------------------------------------

    return render(
        request,
        "core/dashboard.html",
        context,
    )