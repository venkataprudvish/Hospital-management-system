from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from authentication.models import Profile

from .models import Doctor, Patient


class RecordsAuthorizationTests(TestCase):

    def setUp(self):
        # =====================================================
        # PATIENT A
        # =====================================================

        self.patient_a_user = User.objects.create_user(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        self.patient_a = Patient.objects.create(
            user=self.patient_a_user,
            first_name="A",
            last_name="Patient",
        )

        # =====================================================
        # PATIENT B
        # =====================================================

        self.patient_b_user = User.objects.create_user(
            username="patient_b",
            password="B-strong-test-password-123",
        )

        self.patient_b = Patient.objects.create(
            user=self.patient_b_user,
            first_name="B",
            last_name="Patient",
        )

        # =====================================================
        # ADMIN
        # =====================================================

        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="Admin-strong-test-password-123",
        )

        self.admin_user.profile.role = Profile.ROLE_ADMIN
        self.admin_user.profile.save()

        # =====================================================
        # NURSE
        # =====================================================

        self.nurse_user = User.objects.create_user(
            username="nurse_test",
            password="Nurse-strong-test-password-123",
        )

        self.nurse_user.profile.role = Profile.ROLE_NURSE
        self.nurse_user.profile.save()

        # =====================================================
        # DOCTORS
        # =====================================================

        self.available_doctor = Doctor.objects.create(
            first_name="Available",
            last_name="Doctor",
            specialization="General Medicine",
            is_available=True,
        )

        self.unavailable_doctor = Doctor.objects.create(
            first_name="Unavailable",
            last_name="Doctor",
            specialization="Cardiology",
            is_available=False,
        )

    # =========================================================
    # PATIENT ISOLATION
    # =========================================================

    def test_patient_sees_only_own_record(self):
        self.client.login(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        response = self.client.get(
            reverse("patient-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "A Patient",
        )

        self.assertNotContains(
            response,
            "B Patient",
        )

    def test_second_patient_cannot_see_first_patient_record(self):
        self.client.login(
            username="patient_b",
            password="B-strong-test-password-123",
        )

        response = self.client.get(
            reverse("patient-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "B Patient",
        )

        self.assertNotContains(
            response,
            "A Patient",
        )

    # =========================================================
    # STAFF PATIENT ACCESS
    # =========================================================

    def test_admin_can_see_all_patient_records(self):
        self.client.login(
            username="admin_test",
            password="Admin-strong-test-password-123",
        )

        response = self.client.get(
            reverse("patient-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "A Patient",
        )

        self.assertContains(
            response,
            "B Patient",
        )

    def test_nurse_can_see_all_patient_records(self):
        self.client.login(
            username="nurse_test",
            password="Nurse-strong-test-password-123",
        )

        response = self.client.get(
            reverse("patient-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "A Patient",
        )

        self.assertContains(
            response,
            "B Patient",
        )

    # =========================================================
    # PATIENT CREATION AUTHORIZATION
    # =========================================================

    def test_patient_cannot_create_patient_record(self):
        self.client.login(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        response = self.client.get(
            reverse("patient-create")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_access_patient_creation(self):
        self.client.login(
            username="admin_test",
            password="Admin-strong-test-password-123",
        )

        response = self.client.get(
            reverse("patient-create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # =========================================================
    # DOCTOR VISIBILITY
    # =========================================================

    def test_patient_sees_only_available_doctors(self):
        self.client.login(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        response = self.client.get(
            reverse("doctor-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Available Doctor",
        )

        self.assertNotContains(
            response,
            "Unavailable Doctor",
        )

    def test_admin_can_see_all_doctors(self):
        self.client.login(
            username="admin_test",
            password="Admin-strong-test-password-123",
        )

        response = self.client.get(
            reverse("doctor-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Available Doctor",
        )

        self.assertContains(
            response,
            "Unavailable Doctor",
        )

    # =========================================================
    # DOCTOR CREATION AUTHORIZATION
    # =========================================================

    def test_patient_cannot_create_doctor(self):
        self.client.login(
            username="patient_a",
            password="A-strong-test-password-123",
        )

        response = self.client.get(
            reverse("doctor-create")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_access_doctor_creation(self):
        self.client.login(
            username="admin_test",
            password="Admin-strong-test-password-123",
        )

        response = self.client.get(
            reverse("doctor-create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # =========================================================
    # UNAUTHENTICATED ACCESS
    # =========================================================

    def test_anonymous_user_is_redirected_from_patient_list(self):
        response = self.client.get(
            reverse("patient-list")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_anonymous_user_is_redirected_from_doctor_list(self):
        response = self.client.get(
            reverse("doctor-list")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_anonymous_user_is_redirected_from_patient_creation(self):
        response = self.client.get(
            reverse("patient-create")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_anonymous_user_is_redirected_from_doctor_creation(self):
        response = self.client.get(
            reverse("doctor-create")
        )

        self.assertEqual(
            response.status_code,
            302,
        )