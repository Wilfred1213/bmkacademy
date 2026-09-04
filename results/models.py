from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)


class AssessmentComponent(models.Model):

    term = models.ForeignKey(
        "academics.Term",
        on_delete=models.CASCADE,
        related_name="assessment_components",
    )

    name = models.CharField(
        max_length=100,
    )

    max_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )

    order = models.PositiveIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "term",
                    "name",
                ],
                name="unique_assessment_component_per_term",
            ),

        ]

        ordering = [
            "order",
            "name",
        ]

    def __str__(self):

        return (
            f"{self.term} - "
            f"{self.name}"
        )

class StudentSubjectResult(models.Model):

    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="subject_results",
    )

    class_subject = models.ForeignKey(
        "academics.ClassSubject",
        on_delete=models.PROTECT,
        related_name="student_results",
    )

    total_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    grade = models.CharField(
        max_length=10,
        blank=True,
    )

    remark = models.CharField(
        max_length=255,
        blank=True,
    )

    def clean(self):

        if (
            self.class_subject.school_class_id
            != self.enrollment.school_class_id
        ):

            raise ValidationError(
                "The selected subject does not belong "
                "to the student's enrolled class."
            )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "enrollment",
                    "class_subject",
                ],
                name="unique_student_subject_result",
            ),

        ]

    def __str__(self):

        return (
            f"{self.enrollment.student} - "
            f"{self.class_subject}"
        )

class AssessmentScore(models.Model):

    student_subject_result = models.ForeignKey(
        StudentSubjectResult,
        on_delete=models.CASCADE,
        related_name="assessment_scores",
    )

    assessment_component = models.ForeignKey(
        AssessmentComponent,
        on_delete=models.PROTECT,
        related_name="assessment_scores",
    )

    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
    )

    def clean(self):

        if (
            self.assessment_component.term_id
            != self.student_subject_result.enrollment.term_id
        ):

            raise ValidationError(
                "The assessment component does not belong "
                "to the student's enrollment term."
            )

        if (
            self.score
            > self.assessment_component.max_score
        ):

            raise ValidationError(
                {
                    "score": (
                        f"Score cannot exceed "
                        f"{self.assessment_component.max_score}."
                    )
                }
            )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "student_subject_result",
                    "assessment_component",
                ],
                name="unique_result_assessment_component",
            ),

        ]

    def __str__(self):

        return (
            f"{self.student_subject_result} - "
            f"{self.assessment_component}"
        )

class BehaviourCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    order = models.PositiveIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:

        ordering = [
            "order",
            "name",
        ]

    def __str__(self):

        return self.name

class StudentBehaviourRating(models.Model):

    enrollment = models.ForeignKey(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="behaviour_ratings",
    )

    behaviour_category = models.ForeignKey(
        BehaviourCategory,
        on_delete=models.PROTECT,
        related_name="student_ratings",
    )

    # rating = models.PositiveSmallIntegerField()
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "enrollment",
                    "behaviour_category",
                ],
                name="unique_student_behaviour_rating",
            ),

        ]

    def __str__(self):

        return (
            f"{self.enrollment.student} - "
            f"{self.behaviour_category}"
        )


class StudentTermReport(models.Model):

    enrollment = models.OneToOneField(
        "students.Enrollment",
        on_delete=models.CASCADE,
        related_name="term_report",
    )

    teacher_remark = models.TextField(
        blank=True,
    )

    head_teacher_remark = models.TextField(
        blank=True,
    )

    next_term_begins = models.DateField(
        null=True,
        blank=True,
    )

    is_published = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):

        return (
            f"{self.enrollment.student} - "
            f"{self.enrollment.term}"
        )