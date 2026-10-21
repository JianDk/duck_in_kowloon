from django import forms
from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r"^[0-9+()\-\s]{6,30}$",
    message="Enter a valid phone number.",
)


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Your name",
                "autocomplete": "name",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "name@example.com",
                "autocomplete": "email",
            }
        ),
    )
    phone = forms.CharField(
        max_length=30,
        required=True,
        validators=[phone_validator],
        widget=forms.TextInput(
            attrs={
                "placeholder": "+45 12 34 56 78",
                "autocomplete": "tel",
            }
        ),
    )
    message = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "Write a short message",
            }
        ),
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_website(self):
        value = self.cleaned_data.get("website", "")
        if value:
            raise forms.ValidationError("Invalid submission.")
        return ""
