from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Student(models.Model):

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("withdrawn", "Withdrawn"),
        ("graduated", "Graduated"),
        ("transferred", "Transferred"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
    )

    first_name = models.CharField(
        max_length=100
    )

    middle_name = models.CharField(
        max_length=100,
        blank=True
    )

    last_name = models.CharField(
        max_length=100
    )

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    admission_number = models.CharField(
        max_length=30,
        unique=True
    )

    date_admitted = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    withdrawal_date = models.DateField(
        null=True,
        blank=True,
    )

    withdrawal_reason = models.TextField(
        blank=True,
    )

    parents = models.ManyToManyField(
        "accounts.ParentProfile",
        related_name="children",
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.first_name} "
            f"{self.last_name} "
            f"({self.admission_number})"
        )

class Enrollment(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.PROTECT,
        related_name="enrollments"
    )

    term = models.ForeignKey(
        "academics.Term",
        on_delete=models.PROTECT,
        related_name="enrollments"
    )

    school_class = models.ForeignKey(
        "academics.SchoolClass",
        on_delete=models.PROTECT,
        related_name="enrollments"
    )

    enrolled_on = models.DateField(
        auto_now_add=True
    )

    is_current = models.BooleanField(
        default=True
    )
    def clean(self):

        if self.term.academic_year_id != self.academic_year_id:
            raise ValidationError(
                "The selected term does not belong to the selected academic year."
            )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "academic_year",
                    "term",
                ],
                name="unique_student_term_enrollment",
            ),
        ]
    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.school_class} - "
            f"{self.academic_year}"
        )