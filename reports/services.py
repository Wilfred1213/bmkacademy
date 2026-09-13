from attendance.models import Attendance

from results.models import (
    StudentSubjectResult,
    StudentBehaviourRating,
    StudentTermReport,
)
from students.models import Enrollment
from decimal import Decimal
from results.services import ResultService

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
    def get_class_performance(
    cls,
    academic_year,
    term,
    school_class,
    ):

        # --------------------------------
        # CLASS SUBJECTS
        # --------------------------------
        # These subjects determine the
        # columns of the report.
        # --------------------------------
        subjects = list(
            school_class.class_subjects
            .filter(
                is_active=True,
            )
            .select_related(
                "subject",
            )
        )

        # --------------------------------
        # STUDENT ENROLLMENTS
        # --------------------------------

        enrollments = (
            Enrollment.objects
            .filter(
                academic_year=academic_year,
                term=term,
                school_class=school_class,
            )
            .select_related(
                "student",
            )
            .prefetch_related(
                "subject_results__class_subject__subject",
            )
            .order_by(
                "student__first_name",
                "student__last_name",
            )
        )

        class_results = []

        # --------------------------------
        # BUILD EACH STUDENT'S RESULT
        # --------------------------------

        for enrollment in enrollments:

            subject_results = (
                enrollment.subject_results.all()
            )

            # Map each result by ClassSubject ID
            result_map = {
                result.class_subject_id: result
                for result in subject_results
            }

            # --------------------------------
            # CREATE SUBJECT SCORES
            # --------------------------------
            # The order follows the class subjects,
            # not whatever results happen to exist.
            # --------------------------------

            subject_scores = []

            for class_subject in subjects:

                result = result_map.get(
                    class_subject.id
                )

                subject_scores.append({
                    "class_subject": class_subject,
                    "result": result,
                    "score": (
                        result.total_score
                        if result
                        and result.total_score is not None
                        else None
                    ),
                })

            # --------------------------------
            # RESULT COMPLETENESS
            # --------------------------------
            
            result_status = (
                ResultService
                .get_student_result_status(
                    enrollment
                )
            )

            is_complete = (
                result_status["is_complete"]
            )

            # --------------------------------
            # TOTAL SCORE
            # --------------------------------

            entered_scores = [
                item["score"]
                for item in subject_scores
                if item["score"] is not None
            ]

            total_score = sum(
                entered_scores,
                Decimal("0"),
            )

            # --------------------------------
            # AVERAGE
            # --------------------------------
            # Only a complete result gets
            # an official average.
            # --------------------------------

            if is_complete and subjects:

                average = (
                    total_score
                    / Decimal(len(subjects))
                )

            else:

                average = None

            class_results.append({
                "enrollment": enrollment,

                "student": enrollment.student,

                "subject_scores": subject_scores,

                "total_score": (
                    total_score
                    if entered_scores
                    else None
                ),

                "average": average,

                "is_complete": is_complete,

                "result_status": result_status,

                "position": None,
            })

        # --------------------------------
        # RANK ONLY COMPLETE STUDENTS
        # --------------------------------

        ranked_students = [
            item
            for item in class_results
            if item["is_complete"]
            and item["average"] is not None
        ]

        ranked_students.sort(
            key=lambda item: item["average"],
            reverse=True,
        )

        # --------------------------------
        # ASSIGN POSITIONS
        # --------------------------------

        position = 0
        previous_average = None

        for index, item in enumerate(
            ranked_students,
            start=1,
        ):

            if item["average"] != previous_average:

                position = index

            item["position"] = position

            previous_average = item["average"]

        # --------------------------------
        # SORT FINAL REPORT
        # --------------------------------
        # Ranked students first,
        # incomplete students afterwards.
        # --------------------------------

        class_results.sort(
            key=lambda item: (
                item["position"] is None,
                item["position"]
                if item["position"] is not None
                else 999999,
                item["student"].first_name,
                item["student"].last_name,
            )
        )

        return {
            "subjects": subjects,
            "class_results": class_results,
        }

