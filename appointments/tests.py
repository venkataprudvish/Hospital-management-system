from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from authentication.models import Profile
from records.models import Doctor, Patient

from .models import Appointment


class AppointmentAuthorizationTests(TestCase):

    def setUp(self):
        # -----------------------------------------------------
        # Patient A
        # -----------------------------------------------------
        self.patient_a_user = User.objects.create_user(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        self.patient_a = Patient.objects.create(
            user=self.patient_a_user,
            first_name="A",
            last_name="Patient",
        )

        # -----------------------------------------------------
        # Patient B
        # -----------------------------------------------------
        self.patient_b_user = User.objects.create_user(
            username="patient_b",
            password="B-strong-test-password-123",
        )

        self.patient_b = Patient.objects.create(
            user=self.patient_b_user,
            first_name="B",
            last_name="Patient",
        )

        # -----------------------------------------------------
        # Doctor
        # -----------------------------------------------------
        self.doctor_user = User.objects.create_user(
            username="doctor",
            password="D-strong-test-password-123",
        )

        self.doctor_user.profile.role = Profile.ROLE_DOCTOR
        self.doctor_user.profile.save()

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            first_name="Test",
            last_name="Doctor",
            specialization="General",
        )

        # -----------------------------------------------------
        # Patient B's appointment
        # -----------------------------------------------------
        self.appointment = Appointment.objects.create(
            patient=self.patient_b,
            doctor=self.doctor,
            date_time=timezone.now() + timedelta(days=1),
            reason="Checkup",
            created_by=self.patient_b_user,
        )

    # =========================================================
    # PATIENT AUTHORIZATION
    # =========================================================

    def test_patient_cannot_confirm_another_patient_appointment(self):
        self.client.login(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        response = self.client.post(
            reverse(
                "appointment-status",
                args=[
                    self.appointment.pk,
                    "confirmed",
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.STATUS_SCHEDULED,
        )

    def test_patient_cannot_complete_another_patient_appointment(self):
        self.client.login(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        response = self.client.post(
            reverse(
                "appointment-status",
                args=[
                    self.appointment.pk,
                    "completed",
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.STATUS_SCHEDULED,
        )

    def test_patient_cannot_cancel_another_patient_appointment(self):
        self.client.login(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        response = self.client.post(
            reverse(
                "appointment-status",
                args=[
                    self.appointment.pk,
                    "cancelled",
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.STATUS_SCHEDULED,
        )

    # =========================================================
    # PATIENT OWN APPOINTMENT
    # =========================================================

    def test_patient_can_cancel_own_appointment(self):
        own_appointment = Appointment.objects.create(
            patient=self.patient_a,
            doctor=self.doctor,
            date_time=timezone.now() + timedelta(days=2),
            reason="Own appointment",
            created_by=self.patient_a_user,
        )

        self.client.login(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        response = self.client.post(
            reverse(
                "appointment-status",
                args=[
                    own_appointment.pk,
                    "cancelled",
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        own_appointment.refresh_from_db()

        self.assertEqual(
            own_appointment.status,
            Appointment.STATUS_CANCELLED,
        )

    def test_patient_cannot_confirm_own_appointment(self):
        own_appointment = Appointment.objects.create(
            patient=self.patient_a,
            doctor=self.doctor,
            date_time=timezone.now() + timedelta(days=2),
            reason="Own appointment",
            created_by=self.patient_a_user,
        )

        self.client.login(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        response = self.client.post(
            reverse(
                "appointment-status",
                args=[
                    own_appointment.pk,
                    "confirmed",
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        own_appointment.refresh_from_db()

        self.assertEqual(
            own_appointment.status,
            Appointment.STATUS_SCHEDULED,
        )

    # =========================================================
    # DOCTOR AUTHORIZATION
    # =========================================================

    def test_doctor_can_confirm_own_appointment(self):
        self.client.login(
            username="doctor",
            password="D-strong-test-password-123",
        )

        response = self.client.post(
            reverse(
                "appointment-status",
                args=[
                    self.appointment.pk,
                    "confirmed",
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.STATUS_CONFIRMED,
        )

    def test_doctor_can_complete_own_appointment(self):
        self.appointment.status = (
            Appointment.STATUS_CONFIRMED
        )
        self.appointment.save(
            update_fields=["status"]
        )

        self.client.login(
            username="doctor",
            password="D-strong-test-password-123",
        )

        response = self.client.post(
            reverse(
                "appointment-status",
                args=[
                    self.appointment.pk,
                    "completed",
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.STATUS_COMPLETED,
        )

    # =========================================================
    # INVALID STATUS
    # =========================================================

    def test_invalid_status_is_rejected(self):
        self.client.login(
            username="doctor",
            password="D-strong-test-password-123",
        )

        response = self.client.post(
            reverse(
                "appointment-status",
                args=[
                    self.appointment.pk,
                    "hacked",
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.STATUS_SCHEDULED,
        )

    # =========================================================
    # HTTP METHOD SECURITY
    # =========================================================

    def test_status_change_cannot_be_done_with_get(self):
        self.client.login(
            username="doctor",
            password="D-strong-test-password-123",
        )

        response = self.client.get(
            reverse(
                "appointment-status",
                args=[
                    self.appointment.pk,
                    "confirmed",
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.appointment.refresh_from_db()

        self.assertEqual(
            self.appointment.status,
            Appointment.STATUS_SCHEDULED,
        )