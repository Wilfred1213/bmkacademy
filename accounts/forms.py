from django import forms

from .models import ParentProfile, User
from teachers.models import Teacher


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


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter first name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter last name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter email address",
                }
            ),
        }


class TeacherProfileForm(forms.ModelForm):

    class Meta:
        model = Teacher

        fields = [
            "qualification",
            "phone",
        ]

        widgets = {
            "qualification": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter qualification",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                }
            ),
        }