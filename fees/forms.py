from django import forms

from .models import FeeInvoice


class FeeInvoiceForm(forms.ModelForm):

    class Meta:
        model = FeeInvoice

        fields = [
            "enrollment",
            "description",
            "amount",
            "due_date",
        ]

        widgets = {
            "enrollment": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2026/2027 School Fees",
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "due_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
        }