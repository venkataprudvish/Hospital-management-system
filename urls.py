from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from appointments.views import (
    appointment_list,
    book_appointment,
    update_status,
)
from authentication.views import (
    login_view,
    logout_view,
    register_view,
)
from billing.views import (
    billing_list,
    create_bill,
    pay_bill,
)
from core.views import dashboard
from records.views import (
    doctor_create,
    doctor_list,
    patient_create,
    patient_list,
)


urlpatterns = [
    # ---------------------------------------------------------
    # Django administration
    # ---------------------------------------------------------
    path(
        "admin/",
        admin.site.urls,
    ),

    # ---------------------------------------------------------
    # Dashboard
    # ---------------------------------------------------------
    path(
        "",
        RedirectView.as_view(
            pattern_name="dashboard",
            permanent=False,
        ),
    ),

    path(
        "dashboard/",
        dashboard,
        name="dashboard",
    ),

    # ---------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------
    path(
        "login/",
        login_view,
        name="login",
    ),

    path(
        "register/",
        register_view,
        name="register",
    ),

    path(
        "logout/",
        logout_view,
        name="logout",
    ),

    # ---------------------------------------------------------
    # Patient records
    # ---------------------------------------------------------
    path(
        "patients/",
        patient_list,
        name="patient-list",
    ),

    path(
        "patients/add/",
        patient_create,
        name="patient-create",
    ),

    # ---------------------------------------------------------
    # Doctor records
    # ---------------------------------------------------------
    path(
        "doctors/",
        doctor_list,
        name="doctor-list",
    ),

    path(
        "doctors/add/",
        doctor_create,
        name="doctor-create",
    ),

    # ---------------------------------------------------------
    # Appointments
    # ---------------------------------------------------------
    path(
        "appointments/",
        appointment_list,
        name="appointment-list",
    ),

    path(
        "appointments/book/",
        book_appointment,
        name="book-appointment",
    ),

    path(
        "appointments/<int:pk>/<str:status>/",
        update_status,
        name="appointment-status",
    ),

    # ---------------------------------------------------------
    # Billing
    # ---------------------------------------------------------
    path(
        "billing/",
        billing_list,
        name="billing-list",
    ),

    path(
        "billing/add/",
        create_bill,
        name="bill-create",
    ),

    path(
        "billing/<int:pk>/pay/",
        pay_bill,
        name="bill-pay",
    ),
]