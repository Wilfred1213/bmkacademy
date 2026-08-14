from django.db import transaction

from .models import Student, Enrollment
from django.utils import timezone


class StudentService:

    @staticmethod
    def get_current_enrollment(student):

        enrollment = (
            Enrollment.objects
            .filter(
                student=student,
                is_current=True,
            )
            .select_related(
                "academic_year",
                "term",
                "school_class",
            )
            .first()
        )

        if not enrollment:
            raise ValueError(
                "Student does not have a current enrollment."
            )

        return enrollment

    @classmethod
    @transaction.atomic
    def promote_student(
        cls,
        student,
        new_academic_year,
        new_term,
        new_class,
    ):

        current_enrollment = cls.get_current_enrollment(
            student
        )

        if (
            current_enrollment.academic_year
            == new_academic_year
        ):
            raise ValueError(
                "Student is already enrolled in this academic year."
            )

        current_enrollment.is_current = False

        current_enrollment.save(
            update_fields=["is_current"]
        )

        new_enrollment = Enrollment.objects.create(
            student=student,
            academic_year=new_academic_year,
            term=new_term,
            school_class=new_class,
            is_current=True,
        )

        return new_enrollment

@classmethod
@transaction.atomic
def withdraw_student(cls, student, reason=""):

    if student.status != "active":
        raise ValueError(
            "Only active students can be withdrawn."
        )

    current_enrollment = cls.get_current_enrollment(
        student
    )

    current_enrollment.is_current = False

    current_enrollment.save(
        update_fields=["is_current"]
    )

    student.status = "withdrawn"
    student.withdrawal_date = timezone.now().date()
    student.withdrawal_reason = reason

    student.save(
        update_fields=[
            "status",
            "withdrawal_date",
            "withdrawal_reason",
        ]
    )

    return student