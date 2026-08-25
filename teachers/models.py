from django.db import models

from accounts.models import User

from academics.models import (
    AcademicYear,
    SchoolClass,
    ClassSubject,
)


class Teacher(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )

    employee_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
    )

    qualification = models.CharField(
        max_length=100,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    date_joined = models.DateField()

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.user.get_full_name()

    def generate_employee_id(self):

        year = self.date_joined.year

        prefix = f"BMK-TCH-{year}-"

        last_teacher = (
            Teacher.objects
            .filter(
                employee_id__startswith=prefix
            )
            .order_by(
                "-employee_id"
            )
            .first()
        )

        if last_teacher:

            last_number = int(
                last_teacher.employee_id
                .split("-")[-1]
            )

            next_number = last_number + 1

        else:

            next_number = 1

        return (
            f"{prefix}{next_number:04d}"
        )


    def save(
        self,
        *args,
        **kwargs,
    ):

        if not self.employee_id:

            self.employee_id = (
                self.generate_employee_id()
            )

        super().save(
            *args,
            **kwargs,
        )


class TeachingAssignment(models.Model):

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    class_subject = models.ForeignKey(
        ClassSubject,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "teacher",
                    "class_subject",
                    "academic_year",
                ],
                name="unique_teacher_class_subject_year",
            ),

        ]

    def __str__(self):

        return (
            f"{self.teacher} - "
            f"{self.class_subject} - "
            f"{self.academic_year}"
        )


class ClassTeacherAssignment(models.Model):

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="class_teacher_assignments"
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="class_teacher_assignments"
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="class_teacher_assignments"
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "school_class",
                    "academic_year",
                ],
                name="one_class_teacher_per_class_year",
            ),

        ]

    def __str__(self):

        return (
            f"{self.teacher} - "
            f"{self.school_class} - "
            f"{self.academic_year}"
        )