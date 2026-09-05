from attendance.models import Attendance

from results.models import (
    StudentSubjectResult,
    StudentBehaviourRating,
    StudentTermReport,
)
from students.models import Enrollment


class ReportService:

    @classmethod
    def get_student_term_report(cls, enrollment):

        student = enrollment.student

        subject_results = (
            StudentSubjectResult.objects
            .filter(enrollment=enrollment)
            .select_related("class_subject__subject")
            .prefetch_related(
                "assessment_scores__assessment_component"
            )
            .order_by(
                "class_subject__subject__name"
            )
        )

        behaviour_ratings = (
            StudentBehaviourRating.objects
            .filter(enrollment=enrollment)
            .select_related("behaviour_category")
            .order_by(
                "behaviour_category__order",
                "behaviour_category__name",
            )
        )

        term_report = (
            StudentTermReport.objects
            .filter(enrollment=enrollment)
            .first()
        )

        # -------------------------
        # ATTENDANCE
        # -------------------------

        attendance_records = (
            Attendance.objects
            .filter(
                student=student,
                attendance_date__gte=enrollment.term.start_date,
                attendance_date__lte=enrollment.term.end_date,
            )
            .order_by("attendance_date")
        )

        attendance_summary = {
            "present": attendance_records.filter(
                status="present"
            ).count(),

            "absent": attendance_records.filter(
                status="absent"
            ).count(),

            "late": attendance_records.filter(
                status="late"
            ).count(),

            "excused": attendance_records.filter(
                status="excused"
            ).count(),

            "total": attendance_records.count(),
        }

        return {
            "student": student,
            "enrollment": enrollment,
            "academic_year": enrollment.academic_year,
            "term": enrollment.term,
            "school_class": enrollment.school_class,

            "subject_results": subject_results,
            "behaviour_ratings": behaviour_ratings,
            "term_report": term_report,

            "attendance_summary": attendance_summary,
        }

    @classmethod
    def get_class_performance(cls, academic_year, term, school_class):

        enrollments = (
            Enrollment.objects
            .filter(
                academic_year=academic_year,
                term=term,
                school_class=school_class,
            )
            .select_related("student")
            .prefetch_related(
                "subject_results__class_subject__subject"
            )
            .order_by(
                "student__first_name",
                "student__last_name",
            )
        )

        class_results = []

        for enrollment in enrollments:

            subject_results = enrollment.subject_results.all()

            total_score = sum(
                result.total_score or 0
                for result in subject_results
            )

            subject_count = subject_results.count()

            if subject_count:
                average = total_score / subject_count
            else:
                average = 0

            class_results.append({
                "enrollment": enrollment,
                "student": enrollment.student,
                "subject_results": subject_results,
                "total_score": total_score,
                "average": average,
            })

        # Rank students by average score
        class_results.sort(
            key=lambda item: item["average"],
            reverse=True,
        )

        # Assign positions
        position = 0
        previous_average = None

        for index, item in enumerate(class_results, start=1):

            if item["average"] != previous_average:
                position = index

            item["position"] = position

            previous_average = item["average"]

        return class_results