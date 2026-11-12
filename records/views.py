from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from authentication.models import Profile
from core.utils import has_role

from .forms import DoctorForm, PatientForm
from .models import Doctor, Patient


# Roles allowed to manage/view the complete patient directory.
STAFF_ROLES = (
    Profile.ROLE_OWNER,
    Profile.ROLE_ADMIN,
    Profile.ROLE_NURSE,
    Profile.ROLE_RECEPTIONIST,
)


@login_required
def patient_list(request):
    """
    Display patient records according to the user's role.

    Staff can access the complete patient directory.
    A patient can access only their own patient record.
    Other authenticated users receive an empty queryset.
    """

    if has_role(request.user, *STAFF_ROLES):
        patients = (
            Patient.objects
            .select_related("user")
            .all()
        )

    elif hasattr(request.user, "patient_record"):
        patients = Patient.objects.filter(
            pk=request.user.patient_record.pk
        )

    else:
        patients = Patient.objects.none()

    return render(
        request,
        "records/patients.html",
        {
            "patients": patients,
        },
    )


@login_required
def patient_create(request):
    """
    Create a patient record.

    Only authorized hospital staff may create patient records.
    """

    if not has_role(request.user, *STAFF_ROLES):
        raise PermissionDenied

    form = PatientForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Patient record created.",
        )

        return redirect(
            "patient-list"
        )

    return render(
        request,
        "records/form.html",
        {
            "form": form,
            "title": "Add Patient",
        },
    )


@login_required
def doctor_list(request):
    """
    Display doctors.

    Authorized staff can see all doctors.
    Other authenticated users can see only doctors
    currently marked as available.
    """

    if has_role(request.user, *STAFF_ROLES):
        doctors = (
            Doctor.objects
            .select_related("user")
            .all()
        )

    else:
        doctors = (
            Doctor.objects
            .select_related("user")
            .filter(is_available=True)
        )

    return render(
        request,
        "records/doctors.html",
        {
            "doctors": doctors,
        },
    )


@login_required
def doctor_create(request):
    """
    Create a doctor record.

    Only hospital owners and administrators may
    create doctor records.
    """

    if not has_role(
        request.user,
        Profile.ROLE_OWNER,
        Profile.ROLE_ADMIN,
    ):
        raise PermissionDenied

    form = DoctorForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Doctor record created.",
        )

        return redirect(
            "doctor-list"
        )

    return render(
        request,
        "records/form.html",
        {
            "form": form,
            "title": "Add Doctor",
        },
    )