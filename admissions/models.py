from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

import uuid

class AdmissionApplication(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    RELATIONSHIP_CHOICES = [
        ("father", "Father"),
        ("mother", "Mother"),
        ("guardian", "Guardian"),
        ("other", "Other"),
    ]

    # --------------------------------------------------
    # APPLICANT
    # --------------------------------------------------

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admission_applications",
    )

    # --------------------------------------------------
    # ACADEMIC INFORMATION
    # --------------------------------------------------

    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.PROTECT,
        related_name="admission_applications",
    )
    term = models.ForeignKey(
        "academics.Term",
        on_delete=models.PROTECT,
        related_name="admission_applications",
    )

    desired_class = models.ForeignKey(
        "academics.SchoolClass",
        on_delete=models.PROTECT,
        related_name="admission_applications",
    )

    # --------------------------------------------------
    # STUDENT INFORMATION
    # --------------------------------------------------

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

    previous_school = models.CharField(
        max_length=200,
        blank=True
    )
    student = models.OneToOneField(
        "students.Student",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="admission_application",
    )

    # --------------------------------------------------
    # PARENT / GUARDIAN INFORMATION
    # --------------------------------------------------

    parent_name = models.CharField(
        max_length=150,
        null = True
    )

    parent_phone = models.CharField(
        max_length=20,
        null =True
    )

    parent_email = models.EmailField(
        blank=True
    )

    parent_address = models.TextField(
        blank=True
    )

    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default="guardian",
    )

    # --------------------------------------------------
    # APPLICATION STATUS
    # --------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    # --------------------------------------------------
    # APPLICATION TOKEN
    # --------------------------------------------------

    claim_token = models.UUIDField(
        # default=uuid.uuid4,
        # unique=True,
        editable=False,
        null=True,
        blank=True,
    )

    claim_token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    claimed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    admission_email_sent = models.BooleanField(
        default=False
    )

    admission_email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    admission_email_attempts = models.PositiveIntegerField(
        default=0
    )

    admission_email_last_error = models.TextField(
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.first_name} "
            f"{self.last_name} - "
            f"{self.desired_class} - "
            f"{self.academic_year}"
        )

    def clean(self):

        if (
            self.term
            and self.academic_year
            and self.term.academic_year_id
            != self.academic_year_id
        ):
            raise ValidationError(
                "The selected term does not belong to "
                "the selected academic year."
            )