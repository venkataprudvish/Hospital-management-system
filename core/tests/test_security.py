from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationSecurityTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="A-strong-test-password-123",
        )

    # =========================================================
    # PASSWORD SECURITY
    # =========================================================

    def test_password_is_hashed(self):
        self.assertNotEqual(
            self.user.password,
            "A-strong-test-password-123",
        )

        self.assertTrue(
            self.user.check_password(
                "A-strong-test-password-123"
            )
        )

    # =========================================================
    # DASHBOARD AUTHORIZATION
    # =========================================================

    def test_anonymous_dashboard_redirects(self):
        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            "/login/",
            response.url,
        )

    def test_authenticated_user_can_access_dashboard(self):
        self.client.login(
            username="alice",
            password="A-strong-test-password-123",
        )

        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # =========================================================
    # EMAIL LOGIN
    # =========================================================

    def test_email_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "identifier": "alice@example.com",
                "password": "A-strong-test-password-123",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            "dashboard",
            response.url,
        )

    # =========================================================
    # USERNAME LOGIN
    # =========================================================

    def test_username_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "identifier": "alice",
                "password": "A-strong-test-password-123",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            "dashboard",
            response.url,
        )

    # =========================================================
    # INVALID PASSWORD
    # =========================================================

    def test_invalid_password_is_rejected(self):
        response = self.client.post(
            reverse("login"),
            {
                "identifier": "alice",
                "password": "Wrong-password-123",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )

    # =========================================================
    # UNKNOWN USER
    # =========================================================

    def test_unknown_user_is_rejected(self):
        response = self.client.post(
            reverse("login"),
            {
                "identifier": "doesnotexist",
                "password": "Some-password-123",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )

    # =========================================================
    # LOGOUT
    # =========================================================

    def test_logout_requires_authenticated_user(self):
        response = self.client.post(
            reverse("logout")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            "login",
            response.url,
        )

    def test_authenticated_user_can_logout(self):
        self.client.login(
            username="alice",
            password="A-strong-test-password-123",
        )

        response = self.client.post(
            reverse("logout")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            "login",
            response.url,
        )

        dashboard_response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(
            dashboard_response.status_code,
            302,
        )

        self.assertIn(
            "/login/",
            dashboard_response.url,
        )