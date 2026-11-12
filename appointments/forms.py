from django import forms
from django.utils import timezone
from .models import Appointment
from records.models import Patient, Doctor


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date_time", "reason"]
        widgets = {
            "date_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "reason": forms.TextInput(attrs={"maxlength": 300}),
        }

    def __init__(self, *args, patient_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = patient_queryset if patient_queryset is not None else Patient.objects.all()
        self.fields["doctor"].queryset = Doctor.objects.filter(is_available=True)

    def clean_date_time(self):
        value = self.cleaned_data["date_time"]
        if value <= timezone.now():
            raise forms.ValidationError("Appointment time must be in the future.")
        return value
