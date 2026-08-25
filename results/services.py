from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from students.models import Enrollment

from .models import (
    AssessmentComponent,
    AssessmentScore,
    StudentSubjectResult,
)


class ResultService:

    @classmethod
    @transaction.atomic
    def save_assessment_score(
        cls,
        student_subject_result,
        assessment_component,
        score,
    ):

        score = Decimal(str(score))

        if score < 0:

            raise ValueError(
                "Score cannot be negative."
            )

        if (
            assessment_component.term_id
            != student_subject_result.enrollment.term_id
        ):

            raise ValueError(
                "Assessment component does not belong "
                "to the student's enrollment term."
            )

        if (
            score
            > assessment_component.max_score
        ):

            raise ValueError(
                f"Score cannot exceed "
                f"{assessment_component.max_score}."
            )

        assessment_score, created = (
            AssessmentScore.objects.update_or_create(
                student_subject_result=(
                    student_subject_result
                ),
                assessment_component=(
                    assessment_component
                ),
                defaults={
                    "score": score,
                },
            )
        )

        cls.calculate_subject_total(
            student_subject_result
        )

        return assessment_score
    @classmethod
    def calculate_subject_total(
        cls,
        student_subject_result,
    ):

        total = (
            student_subject_result
            .assessment_scores
            .aggregate(
                total=Sum("score")
            )["total"]
        )

        if total is None:
            total = Decimal("0")

        student_subject_result.total_score = total

        student_subject_result.grade = (
            cls.calculate_grade(total)
        )

        student_subject_result.remark = (
            cls.calculate_remark(total)
        )

        student_subject_result.save(
            update_fields=[
                "total_score",
                "grade",
                "remark",
            ]
        )

        return student_subject_result

    @staticmethod
    def calculate_grade(score):

        if score >= 70:
            return "A"

        if score >= 60:
            return "B"

        if score >= 50:
            return "C"

        if score >= 45:
            return "D"

        if score >= 40:
            return "E"

        return "F"

    @staticmethod
    def calculate_remark(score):

        if score >= 70:
            return "Excellent"

        if score >= 60:
            return "Very Good"

        if score >= 50:
            return "Good"

        if score >= 45:
            return "Fair"

        if score >= 40:
            return "Pass"

        return "Fail"

    @staticmethod
    def get_student_subject_results(
        enrollment,
    ):

        return (
            enrollment
            .subject_results
            .select_related(
                "class_subject",
                "class_subject__subject",
                "class_subject__school_class",
            )
            .prefetch_related(
                "assessment_scores",
                "assessment_scores__assessment_component",
            )
            .order_by(
                "class_subject__subject__name"
            )
        )

    @classmethod
    def calculate_student_summary(
        cls,
        enrollment,
    ):

        results = (
            enrollment
            .subject_results
            .filter(
                total_score__isnull=False
            )
        )

        totals = results.aggregate(
            total=Sum("total_score")
        )

        total_score = (
            totals["total"]
            or Decimal("0")
        )

        subject_count = results.count()

        if subject_count:

            average = round(
                total_score / subject_count,
                2,
            )

        else:

            average = Decimal("0")

        return {
            "total": total_score,
            "average": average,
            "subject_count": subject_count,
        }

    @staticmethod
    def get_class_results(
        school_class,
        academic_year,
        term,
    ):

        return (
            StudentSubjectResult.objects
            .filter(
                enrollment__school_class=school_class,
                enrollment__academic_year=academic_year,
                enrollment__term=term,
            )
            .select_related(
                "enrollment",
                "enrollment__student",
                "class_subject",
                "class_subject__subject",
            )
        )
    @classmethod
    @transaction.atomic
    def save_class_results(
        cls,
        academic_year,
        term,
        school_class,
        class_subject,
        result_data,
    ):

        enrollments = (
            Enrollment.objects
            .filter(
                academic_year=academic_year,
                term=term,
                school_class=school_class,
                is_current=True,
                student__status="active",
            )
            .select_related(
                "student",
            )
        )

        assessment_components = (
            AssessmentComponent.objects
            .filter(
                term=term,
                is_active=True,
            )
            .order_by(
                "order",
                "name",
            )
        )

        for enrollment in enrollments:

            student_subject_result, created = (
                StudentSubjectResult.objects
                .get_or_create(
                    enrollment=enrollment,
                    class_subject=class_subject,
                )
            )

            for component in assessment_components:

                score = result_data.get(
                    f"score_{enrollment.id}_{component.id}"
                )

                # Empty field means no score entered
                if score in (
                    None,
                    "",
                ):
                    continue

                cls.save_assessment_score(
                    student_subject_result=(
                        student_subject_result
                    ),
                    assessment_component=component,
                    score=score,
                )

    
    @staticmethod
    def get_student_term_result(enrollment):
        position_data = ResultService.get_student_position(
        enrollment
        )
        subject_results = (
            enrollment
            .subject_results
            .select_related(
                "class_subject",
                "class_subject__subject",
            )
            .prefetch_related(
                "assessment_scores__assessment_component"
            )
            .order_by(
                "class_subject__subject__name"
            )
        )

        total_score = (
            subject_results.aggregate(
                total=Sum("total_score")
            )["total"]
            or Decimal("0")
        )

        scored_subjects = (
            subject_results
            .filter(
                total_score__isnull=False
            )
            .count()
        )

        if scored_subjects:

            average = round(
                total_score / scored_subjects,
                2,
            )

        else:

            average = Decimal("0")

        return {
            "subject_results": subject_results,
            "total_score": total_score,
            "scored_subjects": scored_subjects,
            "average": average,
            "position": position_data["position"],
            "out_of": position_data["out_of"],
        }

    @staticmethod
    def get_student_position(enrollment):

        class_enrollments = (
            Enrollment.objects
            .filter(
                academic_year=enrollment.academic_year,
                term=enrollment.term,
                school_class=enrollment.school_class,
                is_current=True,
                student__status="active",
            )
            .select_related(
                "student"
            )
        )

        student_totals = []

        for class_enrollment in class_enrollments:

            total_score = (
                StudentSubjectResult.objects
                .filter(
                    enrollment=class_enrollment,
                    total_score__isnull=False,
                )
                .aggregate(
                    total=Sum("total_score")
                )["total"]
                or Decimal("0")
            )

            student_totals.append(
                {
                    "enrollment_id": (
                        class_enrollment.id
                    ),
                    "total_score": total_score,
                }
            )

        student_totals = sorted(
            student_totals,
            key=lambda item: item["total_score"],
            reverse=True,
        )

        position = None

        for index, item in enumerate(
            student_totals,
            start=1,
        ):

            if (
                item["enrollment_id"]
                == enrollment.id
            ):

                position = index
                break

        return {
            "position": position,
            "out_of": len(student_totals),
        }