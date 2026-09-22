from django import forms


class AnnouncementForm(forms.Form):

    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. School Resumes Monday",
            }
        ),
    )

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Write your announcement here...",
            }
        ),
    )

    recipient_group = forms.ChoiceField(
        choices=[
            ("parents", "All Parents"),
            ("teachers", "All Teachers"),
            ("students", "All Students"),
            ("everyone", "Everyone"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )