from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from authentication.models import Profile
from core.utils import has_role
from .forms import AppointmentForm
from .models import Appointment
from records.models import Patient

STAFF = (Profile.ROLE_OWNER, Profile.ROLE_ADMIN, Profile.ROLE_NURSE, Profile.ROLE_RECEPTIONIST)


@login_required
def appointment_list(request):
    qs = Appointment.objects.select_related("patient", "doctor", "created_by")
    if request.user.is_superuser or has_role(request.user, *STAFF):
        appointments = qs.all()
    elif hasattr(request.user, "doctor_record"):
        appointments = qs.filter(doctor=request.user.doctor_record)
    elif hasattr(request.user, "patient_record"):
        appointments = qs.filter(patient=request.user.patient_record)
    else:
        appointments = qs.none()
    return render(request, "appointments/list.html", {"appointments": appointments})


@login_required
def book_appointment(request):
    if hasattr(request.user, "patient_record") and not has_role(request.user, *STAFF):
        patient_qs = Patient.objects.filter(pk=request.user.patient_record.pk)
    elif has_role(request.user, *STAFF):
        patient_qs = Patient.objects.all()
    else:
        raise PermissionDenied
    form = AppointmentForm(request.POST or None, patient_queryset=patient_qs)
    if request.method == "POST" and form.is_valid():
        appointment = form.save(commit=False)
        if hasattr(request.user, "patient_record") and not has_role(request.user, *STAFF):
            appointment.patient = request.user.patient_record
        conflict = Appointment.objects.filter(doctor=appointment.doctor, date_time=appointment.date_time).exclude(status=Appointment.STATUS_CANCELLED).exists()
        if conflict:
            form.add_error("date_time", "That doctor already has an appointment at this time.")
        else:
            appointment.created_by = request.user
            appointment.save()
            messages.success(request, "Appointment booked successfully.")
            return redirect("appointment-list")
    return render(request, "appointments/form.html", {"form": form})


@login_required
def update_status(request, pk, status):
    if request.method != "POST":
        raise PermissionDenied
    appointment = get_object_or_404(Appointment, pk=pk)
    allowed = False
    if request.user.is_superuser or has_role(request.user, *STAFF):
        allowed = True
    elif hasattr(request.user, "doctor_record") and appointment.doctor_id == request.user.doctor_record.id and status in {"confirmed", "completed", "cancelled"}:
        allowed = True
    elif hasattr(request.user, "patient_record") and appointment.patient_id == request.user.patient_record.id and status == "cancelled":
        allowed = True
    if not allowed:
        raise PermissionDenied
    if status not in dict(Appointment.STATUS_CHOICES):
        raise PermissionDenied
    appointment.status = status
    appointment.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Appointment marked {appointment.get_status_display().lower()}.")
    return redirect("appointment-list")
