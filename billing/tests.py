from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from appointments.models import Appointment
from authentication.models import Profile
from records.models import Doctor, Patient

from .forms import BillForm
from .models import Bill


class BillingSecurityTests(TestCase):

    def setUp(self):
        # =====================================================
        # PATIENT A
        # =====================================================

        self.patient_a_user = User.objects.create_user(
            username="patient_a",
            password="Patient-A-strong-password-123",
        )

        self.patient_a_user.profile.role = (
            Profile.ROLE_PATIENT
        )
        self.patient_a_user.profile.save()

        self.patient_a = Patient.objects.create(
            user=self.patient_a_user,
            first_name="Patient",
            last_name="A",
        )

        # =====================================================
        # PATIENT B
        # =====================================================

        self.patient_b_user = User.objects.create_user(
            username="patient_b",
            password="Patient-B-strong-password-123",
        )

        self.patient_b_user.profile.role = (
            Profile.ROLE_PATIENT
        )
        self.patient_b_user.profile.save()

        self.patient_b = Patient.objects.create(
            user=self.patient_b_user,
            first_name="Patient",
            last_name="B",
        )

        # =====================================================
        # ACCOUNTANT
        # =====================================================

        self.staff_user = User.objects.create_user(
            username="accountant",
            password="Accountant-strong-password-123",
        )

        self.staff_user.profile.role = (
            Profile.ROLE_ACCOUNTANT
        )
        self.staff_user.profile.save()

        # =====================================================
        # DOCTOR
        # =====================================================

        self.doctor = Doctor.objects.create(
            first_name="Test",
            last_name="Doctor",
            specialization="General Medicine",
        )

        # =====================================================
        # APPOINTMENT
        # =====================================================

        self.appointment_a = Appointment.objects.create(
            patient=self.patient_a,
            doctor=self.doctor,
            date_time="2030-01-01T10:00:00Z",
            reason="Test appointment A",
            created_by=self.staff_user,
        )

        # =====================================================
        # BILLS
        # =====================================================

        self.bill_a = Bill.objects.create(
            patient=self.patient_a,
            appointment=self.appointment_a,
            description="Consultation",
            amount=Decimal("500.00"),
            created_by=self.staff_user,
        )

        self.bill_b = Bill.objects.create(
            patient=self.patient_b,
            description="Consultation",
            amount=Decimal("750.00"),
            created_by=self.staff_user,
        )

    # =========================================================
    # BILL VISIBILITY
    # =========================================================

    def test_patient_sees_only_own_bills(self):
        self.client.login(
            username="patient_a",
            password="Patient-A-strong-password-123",
        )

        response = self.client.get(
            reverse("billing-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "500.00",
        )

        self.assertNotContains(
            response,
            "750.00",
        )

    def test_second_patient_cannot_see_first_patient_bill(self):
        self.client.login(
            username="patient_b",
            password="Patient-B-strong-password-123",
        )

        response = self.client.get(
            reverse("billing-list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "750.00",
        )

        self.assertNotContains(
            response,
            "500.00",
        )

    # =========================================================
    # BILL PAYMENT AUTHORIZATION
    # =========================================================

    def test_patient_cannot_pay_bill(self):
        self.client.login(
            username="patient_a",
            password="Patient-A-strong-password-123",
        )

        response = self.client.post(
            reverse(
                "bill-pay",
                kwargs={"pk": self.bill_a.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.bill_a.refresh_from_db()

        self.assertEqual(
            self.bill_a.status,
            Bill.STATUS_PENDING,
        )

        self.assertIsNone(
            self.bill_a.paid_at,
        )

    def test_accountant_can_pay_bill(self):
        self.client.login(
            username="accountant",
            password="Accountant-strong-password-123",
        )

        response = self.client.post(
            reverse(
                "bill-pay",
                kwargs={"pk": self.bill_a.pk},
            )
        )

        self.assertRedirects(
            response,
            reverse("billing-list"),
        )

        self.bill_a.refresh_from_db()

        self.assertEqual(
            self.bill_a.status,
            Bill.STATUS_PAID,
        )

        self.assertIsNotNone(
            self.bill_a.paid_at,
        )

    def test_paid_bill_cannot_be_paid_again_as_new_transition(self):
        self.bill_a.status = Bill.STATUS_PAID
        self.bill_a.save(
            update_fields=["status"]
        )

        self.client.login(
            username="accountant",
            password="Accountant-strong-password-123",
        )

        response = self.client.post(
            reverse(
                "bill-pay",
                kwargs={"pk": self.bill_a.pk},
            )
        )

        self.assertRedirects(
            response,
            reverse("billing-list"),
        )

        self.bill_a.refresh_from_db()

        self.assertEqual(
            self.bill_a.status,
            Bill.STATUS_PAID,
        )

    # =========================================================
    # BILL CREATION AUTHORIZATION
    # =========================================================

    def test_patient_cannot_access_bill_creation(self):
        self.client.login(
            username="patient_a",
            password="Patient-A-strong-password-123",
        )

        response = self.client.get(
            reverse("bill-create")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_accountant_can_access_bill_creation(self):
        self.client.login(
            username="accountant",
            password="Accountant-strong-password-123",
        )

        response = self.client.get(
            reverse("bill-create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # =========================================================
    # BILL FORM INTEGRITY
    # =========================================================

    def test_bill_form_rejects_patient_appointment_mismatch(self):
        form = BillForm(
            data={
                "patient": self.patient_b.pk,
                "appointment": self.appointment_a.pk,
                "description": "Invalid billing",
                "amount": "100.00",
            },
            patient_queryset=Patient.objects.all(),
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "appointment",
            form.errors,
        )

    def test_negative_amount_is_rejected_by_form(self):
        form = BillForm(
            data={
                "patient": self.patient_a.pk,
                "appointment": self.appointment_a.pk,
                "description": "Invalid amount",
                "amount": "-100.00",
            },
            patient_queryset=Patient.objects.all(),
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "amount",
            form.errors,
        )

    def test_zero_amount_is_allowed(self):
        form = BillForm(
            data={
                "patient": self.patient_a.pk,
                "appointment": self.appointment_a.pk,
                "description": "Zero amount test",
                "amount": "0.00",
            },
            patient_queryset=Patient.objects.all(),
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_text(),
        )

    # =========================================================
    # DATABASE INTEGRITY
    # =========================================================

    def test_database_rejects_negative_bill_amount(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Bill.objects.create(
                    patient=self.patient_a,
                    appointment=self.appointment_a,
                    description="Invalid negative bill",
                    amount=Decimal("-1.00"),
                    created_by=self.staff_user,
                )

    # =========================================================
    # UNAUTHENTICATED ACCESS
    # =========================================================

    def test_anonymous_user_is_redirected_from_billing(self):
        response = self.client.get(
            reverse("billing-list")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_anonymous_user_is_redirected_from_bill_creation(self):
        response = self.client.get(
            reverse("bill-create")
        )

        self.assertEqual(
            response.status_code,
            302,
        )