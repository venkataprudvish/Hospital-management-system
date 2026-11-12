from django.contrib import admin
from .models import Patient, Doctor


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "date_of_birth", "contact_number", "created_at")
    search_fields = ("first_name", "last_name", "contact_number", "user__username")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "specialization", "is_available", "created_at")
    list_filter = ("specialization", "is_available")
    search_fields = ("first_name", "last_name", "license_number", "user__username")
