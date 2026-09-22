from django import forms
from .models import ParentProfile


class ParentProfileForm(forms.ModelForm):

    class Meta:
        model = ParentProfile
        fields = [
            "phone",
            "address",
            "occupation",
        ]

        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter your address",
                }
            ),
            "occupation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter occupation",
                }
            ),
        }