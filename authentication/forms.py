from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from records.models import Patient

from .models import Profile


class LoginForm(forms.Form):
    identifier = forms.CharField(
        max_length=254,
        label="Username or email",
        strip=True,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "autocapitalize": "none",
                "spellcheck": "false",
            }
        ),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
            }
        ),
        max_length=128,
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None

        super().__init__(
            *args,
            **kwargs,
        )

    def clean(self):
        cleaned_data = super().clean()

        identifier = cleaned_data.get(
            "identifier",
            "",
        ).strip()

        password = cleaned_data.get("password")

        if not identifier or not password:
            return cleaned_data

        username = identifier

        if "@" in identifier:
            user = (
                User.objects
                .filter(
                    email__iexact=identifier,
                )
                .only("username")
                .first()
            )

            if user is not None:
                username = user.username

        self.user_cache = authenticate(
            self.request,
            username=username,
            password=password,
        )

        if (
            self.user_cache is None
            or not self.user_cache.is_active
        ):
            raise forms.ValidationError(
                "Invalid credentials."
            )

        return cleaned_data

    def get_user(self):
        return self.user_cache


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=80,
        strip=True,
    )

    last_name = forms.CharField(
        max_length=80,
        strip=True,
    )

    email = forms.EmailField(
        max_length=254,
    )

    phone = forms.CharField(
        max_length=30,
        required=False,
        strip=True,
    )

    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "password1",
            "password2",
        )

    def clean_first_name(self):
        value = self.cleaned_data["first_name"].strip()

        if not value:
            raise forms.ValidationError(
                "First name is required."
            )

        return value

    def clean_last_name(self):
        value = self.cleaned_data["last_name"].strip()

        if not value:
            raise forms.ValidationError(
                "Last name is required."
            )

        return value

    def clean_email(self):
        email = (
            self.cleaned_data["email"]
            .strip()
            .lower()
        )

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_username(self):
        username = (
            self.cleaned_data["username"]
            .strip()
        )

        if not username:
            raise forms.ValidationError(
                "Username is required."
            )

        if User.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError(
                "This username is already in use."
            )

        return username

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(
            commit=commit
        )

        if not commit:
            return user

        profile, _ = Profile.objects.get_or_create(
            user=user
        )

        profile.phone = self.cleaned_data.get(
            "phone",
            "",
        )

        # Public registration always creates a patient account.
        profile.role = Profile.ROLE_PATIENT

        profile.save(
            update_fields=[
                "phone",
                "role",
                "updated_at",
            ]
        )

        Patient.objects.get_or_create(
            user=user,
            defaults={
                "first_name": self.cleaned_data[
                    "first_name"
                ],
                "last_name": self.cleaned_data[
                    "last_name"
                ],
                "contact_number": self.cleaned_data.get(
                    "phone",
                    "",
                ),
            },
        )

        return user