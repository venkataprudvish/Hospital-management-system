from django import forms

from .models import Patient, Doctor


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "contact_number",
            "address",
            "emergency_contact",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

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

    def clean_contact_number(self):
        return self.cleaned_data.get(
            "contact_number",
            "",
        ).strip()

    def clean_emergency_contact(self):
        return self.cleaned_data.get(
            "emergency_contact",
            "",
        ).strip()


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "first_name",
            "last_name",
            "specialization",
            "license_number",
            "contact_number",
            "room",
            "is_available",
        ]

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

    def clean_specialization(self):
        value = self.cleaned_data["specialization"].strip()

        if not value:
            raise forms.ValidationError(
                "Specialization is required."
            )

        return value

    def clean_license_number(self):
        return self.cleaned_data.get(
            "license_number",
            "",
        ).strip()

    def clean_contact_number(self):
        return self.cleaned_data.get(
            "contact_number",
            "",
        ).strip()

    def clean_room(self):
        return self.cleaned_data.get(
            "room",
            "",
        ).strip()