from django import forms
from academics.models import AcademicYear, Term
from .models import AdmissionApplication
from django.contrib.auth import get_user_model

from django.contrib.auth.password_validation import validate_password


class AdmissionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdmissionApplication
        fields = [
            "academic_year", "term", "desired_class",
            "first_name", "middle_name", "last_name", "date_of_birth",
            "gender", "previous_school",
            "parent_name", "parent_phone", "parent_email",
            "parent_address", "relationship",
        ]
        widgets = {
            "academic_year": forms.Select(attrs={
                    "class": "form-select",
                    "hx-get": "/admissions/admission-terms/",
                    "hx-target": "#id_term",
                    "hx-trigger": "change",
                    "hx-swap": "innerHTML",
                }
            ),
            "term": forms.Select(attrs={"class": "form-select"}),
            "desired_class": forms.Select(attrs={"class": "form-select"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter first name"}),
            "middle_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter middle name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter last name"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "previous_school": forms.TextInput(attrs={"class": "form-control", "placeholder": "Previous school (optional)"}),
            "parent_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Parent / Guardian full name"}),
            "parent_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "080XXXXXXXX"}),
            "parent_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Parent email"}),
            "parent_address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Residential address"}),
            "relationship": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["term"].queryset = Term.objects.none()

        if "academic_year" in self.data:
            try:
                academic_year_id = int(self.data.get("academic_year"))
                self.fields["term"].queryset = Term.objects.filter(
                    academic_year_id=academic_year_id
                ).order_by("start_date")
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields["term"].queryset = self.instance.academic_year.terms.order_by("start_date")
        else:
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                self.fields["academic_year"].initial = current_year
                self.fields["term"].queryset = Term.objects.filter(
                    academic_year=current_year
                ).order_by("start_date")


class ClaimApplicationForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Choose a username",
            }
        ),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create a password",
            }
        ),
        label="Password",
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm your password",
            }
        ),
        label="Confirm Password",
    )

    def clean_username(self):
        username = self.cleaned_data["username"]

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_password(self):
        password = self.cleaned_data["password"]

        validate_password(password)

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:

            if password != confirm_password:

                raise forms.ValidationError(
                    "The passwords do not match."
                )

        return cleaned_data