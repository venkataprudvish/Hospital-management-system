from django import forms

from appointments.models import Appointment
from records.models import Patient

from .models import Bill


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill

        fields = [
            "patient",
            "appointment",
            "description",
            "amount",
        ]

        widgets = {
            "description": forms.TextInput(
                attrs={
                    "maxlength": 200,
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.01",
                }
            ),
        }

    def __init__(
        self,
        *args,
        patient_queryset=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.fields["patient"].queryset = (
            patient_queryset
            if patient_queryset is not None
            else Patient.objects.none()
        )

        self.fields["appointment"].queryset = (
            Appointment.objects
            .select_related("patient", "doctor")
            .order_by("-date_time")
        )

        self.fields["amount"].min_value = 0

    def clean_description(self):
        value = self.cleaned_data["description"].strip()

        if not value:
            raise forms.ValidationError(
                "Description is required."
            )

        return value

    def clean_amount(self):
        value = self.cleaned_data["amount"]

        if value < 0:
            raise forms.ValidationError(
                "Amount cannot be negative."
            )

        return value

    def clean(self):
        cleaned_data = super().clean()

        patient = cleaned_data.get("patient")
        appointment = cleaned_data.get("appointment")

        if patient and appointment:
            if appointment.patient_id != patient.id:
                self.add_error(
                    "appointment",
                    "The selected appointment does not belong to the selected patient.",
                )

        return cleaned_data