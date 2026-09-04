from django import forms
from academics.models import AcademicYear, Term
from .models import AdmissionApplication

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

# from django import forms

# from academics.models import AcademicYear, Term, SchoolClass
# from .models import AdmissionApplication


# class AdmissionApplicationForm(forms.ModelForm):

#     class Meta:
#         model = AdmissionApplication

#         fields = [
#             "academic_year",
#             "term",
#             "desired_class",

#             "first_name",
#             "middle_name",
#             "last_name",
#             "date_of_birth",
#             "gender",
#             "previous_school",

#             "parent_name",
#             "parent_phone",
#             "parent_email",
#             "parent_address",
#             "relationship",
#         ]

#         widgets = {

#             "academic_year": forms.Select(
#                 attrs={
#                     "class": "form-select",
#                 }
#             ),

#             "term": forms.Select(
#                 attrs={
#                     "class": "form-select",
#                 }
#             ),

#             "desired_class": forms.Select(
#                 attrs={
#                     "class": "form-select",
#                 }
#             ),

#             "first_name": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter first name",
#                 }
#             ),

#             "middle_name": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter middle name",
#                 }
#             ),

#             "last_name": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Enter last name",
#                 }
#             ),

#             "date_of_birth": forms.DateInput(
#                 attrs={
#                     "class": "form-control",
#                     "type": "date",
#                 }
#             ),

#             "gender": forms.Select(
#                 attrs={
#                     "class": "form-select",
#                 }
#             ),

#             "previous_school": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Previous school (optional)",
#                 }
#             ),

#             "parent_name": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Parent / Guardian full name",
#                 }
#             ),

#             "parent_phone": forms.TextInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "080XXXXXXXX",
#                 }
#             ),

#             "parent_email": forms.EmailInput(
#                 attrs={
#                     "class": "form-control",
#                     "placeholder": "Parent email",
#                 }
#             ),

#             "parent_address": forms.Textarea(
#                 attrs={
#                     "class": "form-control",
#                     "rows": 3,
#                     "placeholder": "Residential address",
#                 }
#             ),

#             "relationship": forms.Select(
#                 attrs={
#                     "class": "form-select",
#                 }
#             ),
#         }

#     def __init__(self, *args, **kwargs):

#         super().__init__(*args, **kwargs)

#         self.fields["term"].queryset = Term.objects.none()

#         if "academic_year" in self.data:

#             try:

#                 academic_year_id = int(
#                     self.data.get("academic_year")
#                 )

#                 self.fields["term"].queryset = (
#                     Term.objects
#                     .filter(
#                         academic_year_id=academic_year_id
#                     )
#                     .order_by("start_date")
#                 )

#             except (
#                 ValueError,
#                 TypeError,
#             ):

#                 pass

#         elif self.instance.pk:

#             self.fields["term"].queryset = (
#                 Term.objects
#                 .filter(
#                     academic_year=self.instance.academic_year
#                 )
#                 .order_by("start_date")
#             )

#         else:

#             current_year = (
#                 AcademicYear.objects
#                 .filter(is_current=True)
#                 .first()
#             )

#             if current_year:

#                 self.fields["academic_year"].initial = (
#                     current_year
#                 )

#                 self.fields["term"].queryset = (
#                     Term.objects
#                     .filter(
#                         academic_year=current_year
#                     )
#                     .order_by("start_date")
#                 )