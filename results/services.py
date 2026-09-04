from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from students.models import Enrollment
from attendance.models import Attendance
from django.db.models import (
    Count,
    Q,
    Sum,
)


from .models import (
    AssessmentComponent,
    AssessmentScore,
    StudentSubjectResult,
    StudentBehaviourRating,
    StudentTermReport,
)
from academics.models import ClassSubject



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

        # --------------------------------
        # REQUIRED ASSESSMENT COMPONENTS
        # --------------------------------

        required_components = (
            AssessmentComponent.objects
            .filter(
                term=student_subject_result.enrollment.term,
                is_active=True,
            )
            .count()
        )

        # --------------------------------
        # STUDENT SCORES
        # --------------------------------

        scored_components = (
            student_subject_result
            .assessment_scores
            .count()
        )

        # --------------------------------
        # INCOMPLETE SUBJECT
        # --------------------------------

        if (
            scored_components
            < required_components
        ):

            student_subject_result.total_score = None
            student_subject_result.grade = ""
            student_subject_result.remark = ""

            student_subject_result.save(
                update_fields=[
                    "total_score",
                    "grade",
                    "remark",
                ]
            )

            return student_subject_result

        # --------------------------------
        # CALCULATE TOTAL
        # --------------------------------

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

        # --------------------------------
        # GRADE
        # --------------------------------

        student_subject_result.grade = (
            cls.calculate_grade(total)
        )

        # --------------------------------
        # REMARK
        # --------------------------------

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
    # @classmethod
    # def calculate_subject_total(
    #     cls,
    #     student_subject_result,
    # ):

    #     total = (
    #         student_subject_result
    #         .assessment_scores
    #         .aggregate(
    #             total=Sum("score")
    #         )["total"]
    #     )

    #     if total is None:
    #         total = Decimal("0")

    #     student_subject_result.total_score = total

    #     student_subject_result.grade = (
    #         cls.calculate_grade(total)
    #     )

    #     student_subject_result.remark = (
    #         cls.calculate_remark(total)
    #     )

    #     student_subject_result.save(
    #         update_fields=[
    #             "total_score",
    #             "grade",
    #             "remark",
    #         ]
    #     )

    #     return student_subject_result

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

    # @classmethod
    # def calculate_student_summary(
    #     cls,
    #     enrollment,
    # ):

    #     results = (
    #         enrollment
    #         .subject_results
    #         .filter(
    #             total_score__isnull=False
    #         )
    #     )

    #     totals = results.aggregate(
    #         total=Sum("total_score")
    #     )

    #     total_score = (
    #         totals["total"]
    #         or Decimal("0")
    #     )

    #     subject_count = results.count()

    #     if subject_count:

    #         average = round(
    #             total_score / subject_count,
    #             2,
    #         )

    #     else:

    #         average = Decimal("0")

    #     return {
    #         "total": total_score,
    #         "average": average,
    #         "subject_count": subject_count,
    #     }

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
    # --------------------------------
    # GET STUDNET POSITION
    # --------------------------------
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

        # Highest score first
        student_totals.sort(
            key=lambda item: item["total_score"],
            reverse=True,
        )

        # --------------------------------
        # TIE-AWARE RANKING
        # --------------------------------

        position = None

        previous_score = None
        current_position = 0

        for index, item in enumerate(
            student_totals,
            start=1,
        ):

            if (
                previous_score is None
                or item["total_score"] != previous_score
            ):

                current_position = index

            if (
                item["enrollment_id"]
                == enrollment.id
            ):

                position = current_position
                break

            previous_score = item["total_score"]

        return {
            "position": position,
            "out_of": len(student_totals),
        }
    # @staticmethod
    # def get_student_position(enrollment):

    #     class_enrollments = (
    #         Enrollment.objects
    #         .filter(
    #             academic_year=enrollment.academic_year,
    #             term=enrollment.term,
    #             school_class=enrollment.school_class,
    #             is_current=True,
    #             student__status="active",
    #         )
    #         .select_related(
    #             "student"
    #         )
    #     )

    #     student_totals = []

    #     for class_enrollment in class_enrollments:

    #         total_score = (
    #             StudentSubjectResult.objects
    #             .filter(
    #                 enrollment=class_enrollment,
    #                 total_score__isnull=False,
    #             )
    #             .aggregate(
    #                 total=Sum("total_score")
    #             )["total"]
    #             or Decimal("0")
    #         )

    #         student_totals.append(
    #             {
    #                 "enrollment_id": (
    #                     class_enrollment.id
    #                 ),
    #                 "total_score": total_score,
    #             }
    #         )

    #     student_totals = sorted(
    #         student_totals,
    #         key=lambda item: item["total_score"],
    #         reverse=True,
    #     )

    #     position = None

    #     for index, item in enumerate(
    #         student_totals,
    #         start=1,
    #     ):

    #         if (
    #             item["enrollment_id"]
    #             == enrollment.id
    #         ):

    #             position = index
    #             break

    #     return {
    #         "position": position,
    #         "out_of": len(student_totals),
    #     }
    # --------------------------------
    # SAVE BEHAVIOUR RATINGS
    # --------------------------------
    @classmethod
    @transaction.atomic
    def save_behaviour_ratings(
        cls,
        enrollment,
        rating_data,
    ):

        for behaviour_category_id, rating in rating_data.items():

            if rating in (
                None,
                "",
            ):
                continue

            StudentBehaviourRating.objects.update_or_create(
                enrollment=enrollment,
                behaviour_category_id=behaviour_category_id,
                defaults={
                    "rating": rating,
                },
            )

     # --------------------------------
    # GET STUDENT BEHAVIOUR RATINGS
    # --------------------------------

    @staticmethod
    def get_student_behaviour_ratings(
        enrollment,
    ):

        return (
            enrollment
            .behaviour_ratings
            .select_related(
                "behaviour_category"
            )
            .order_by(
                "behaviour_category__order",
                "behaviour_category__name",
            )
        )

    # --------------------------------
    # STUDENT SUBJECT RESULTS
    # --------------------------------

    @staticmethod
    def get_student_subject_results(enrollment):

        return (
            StudentSubjectResult.objects
            .filter(
                enrollment=enrollment,
            )
            .select_related(
                "class_subject",
                "class_subject__subject",
            )
            .prefetch_related(
                "assessment_scores__assessment_component",
            )
            .order_by(
                "class_subject__subject__name"
            )
        )

    @classmethod
    def get_student_result_status(
        cls,
        enrollment,
    ):

        # --------------------------------
        # REQUIRED SUBJECTS
        # --------------------------------

        required_subjects = (
            ClassSubject.objects
            .filter(
                school_class=enrollment.school_class,
                is_active=True,
            )
        )

        required_subject_count = (
            required_subjects.count()
        )

        # --------------------------------
        # REQUIRED ASSESSMENT COMPONENTS
        # --------------------------------

        required_components = (
            AssessmentComponent.objects
            .filter(
                term=enrollment.term,
                is_active=True,
            )
        )

        required_component_ids = set(
            required_components.values_list(
                "id",
                flat=True,
            )
        )

        required_component_count = len(
            required_component_ids
        )

        # --------------------------------
        # STUDENT SUBJECT RESULTS
        # --------------------------------

        subject_results = (
            enrollment
            .subject_results
            .prefetch_related(
                "assessment_scores"
            )
        )

        # --------------------------------
        # CHECK SUBJECTS
        # --------------------------------

        completed_subject_count = 0

        for result in subject_results:

            scored_component_ids = set(
                result
                .assessment_scores
                .filter(
                    assessment_component__is_active=True,
                )
                .values_list(
                    "assessment_component_id",
                    flat=True,
                )
            )

            if (
                scored_component_ids
                == required_component_ids
            ):

                completed_subject_count += 1

        # --------------------------------
        # COMPLETE RESULT?
        # --------------------------------

        is_complete = (
            required_subject_count > 0
            and completed_subject_count
            == required_subject_count
        )

        if is_complete:

            status = "complete"

        else:

            status = "incomplete"

        return {
            "status": status,

            "is_complete": is_complete,

            "required_subject_count": (
                required_subject_count
            ),

            "completed_subject_count": (
                completed_subject_count
            ),

            "required_component_count": (
                required_component_count
            ),
        }
    # @classmethod
    # def get_student_result_status(
    #     cls,
    #     enrollment,
    # ):

    #     # --------------------------------
    #     # REQUIRED SUBJECTS
    #     # --------------------------------

    #     required_subject_count = (
    #         ClassSubject.objects
    #         .filter(
    #             school_class=enrollment.school_class,
    #             is_active=True,
    #         )
    #         .count()
    #     )

    #     # --------------------------------
    #     # REQUIRED ASSESSMENT COMPONENTS
    #     # --------------------------------

    #     required_component_count = (
    #         AssessmentComponent.objects
    #         .filter(
    #             term=enrollment.term,
    #             is_active=True,
    #         )
    #         .count()
    #     )

    #     # --------------------------------
    #     # STUDENT SUBJECT RESULTS
    #     # --------------------------------

    #     subject_results = (
    #         enrollment
    #         .subject_results
    #         .prefetch_related(
    #             "assessment_scores"
    #         )
    #     )

    #     # --------------------------------
    #     # CHECK SUBJECTS
    #     # --------------------------------

    #     completed_subject_count = 0

    #     for result in subject_results:

    #         scored_component_count = (
    #             result
    #             .assessment_scores
    #             .count()
    #         )

    #         if (
    #             scored_component_count
    #             == required_component_count
    #         ):

    #             completed_subject_count += 1

    #     # --------------------------------
    #     # COMPLETE RESULT?
    #     # --------------------------------

    #     is_complete = (
    #         required_subject_count > 0
    #         and completed_subject_count
    #         == required_subject_count
    #     )

    #     if is_complete:

    #         status = "complete"

    #     else:

    #         status = "incomplete"

    #     return {
    #         "status": status,

    #         "is_complete": is_complete,

    #         "required_subject_count": (
    #             required_subject_count
    #         ),

    #         "completed_subject_count": (
    #             completed_subject_count
    #         ),

    #         "required_component_count": (
    #             required_component_count
    #         ),
    #     }
    # --------------------------------
    # STUDENT RESULT SUMMARY
    # --------------------------------
    @classmethod
    def get_student_result_summary(
        cls,
        enrollment,
    ):

        # --------------------------------
        # CHECK RESULT STATUS
        # --------------------------------

        status_data = (
            cls.get_student_result_status(
                enrollment
            )
        )

        # --------------------------------
        # SUBJECT RESULTS
        # --------------------------------

        subject_results = (
            cls.get_student_subject_results(
                enrollment
            )
        )

        # --------------------------------
        # INCOMPLETE RESULT
        # --------------------------------

        if not status_data["is_complete"]:

            return {
                "subject_results": subject_results,

                "total_score": None,

                "scored_subject_count": (
                    status_data[
                        "completed_subject_count"
                    ]
                ),

                "average_score": None,

                "status": "incomplete",
            }

        # --------------------------------
        # COMPLETE RESULT
        # --------------------------------

        total_score = Decimal("0")

        scored_subject_count = 0

        for result in subject_results:

            if result.total_score is not None:

                total_score += (
                    result.total_score
                )

                scored_subject_count += 1

        average_score = Decimal("0")

        if scored_subject_count:

            average_score = (
                total_score
                / scored_subject_count
            )

        return {

            "subject_results": subject_results,

            "total_score": total_score,

            "scored_subject_count": (
                scored_subject_count
            ),

            "average_score": round(
                average_score,
                2,
            ),

            "status": "complete",
        }

    # @classmethod
    # def get_student_result_summary(
    #     cls,
    #     enrollment,
    # ):

    #     subject_results = (
    #         cls.get_student_subject_results(
    #             enrollment
    #         )
    #     )

    #     total_score = Decimal("0")

    #     scored_subject_count = 0

    #     for result in subject_results:

    #         if result.total_score is not None:

    #             total_score += result.total_score

    #             scored_subject_count += 1

    #     average_score = Decimal("0")

    #     if scored_subject_count:

    #         average_score = (
    #             total_score
    #             / scored_subject_count
    #         )

    #     return {
    #         "subject_results": subject_results,
    #         "total_score": total_score,
    #         "scored_subject_count": (
    #             scored_subject_count
    #         ),
    #         "average_score": round(
    #             average_score,
    #             2,
    #         ),
    #     }

    # --------------------------------
    # CLASS POSITION
    # --------------------------------
    @classmethod
    def get_class_position(
        cls,
        enrollment,
    ):

        class_enrollments = (
            Enrollment.objects
            .filter(
                academic_year=enrollment.academic_year,
                term=enrollment.term,
                school_class=enrollment.school_class,
                is_current=True,
                student__status="active",
            )
        )

        student_results = []

        # --------------------------------
        # GET COMPLETE STUDENTS ONLY
        # --------------------------------

        for class_enrollment in class_enrollments:

            result_summary = (
                cls.get_student_result_summary(
                    class_enrollment
                )
            )

            if result_summary["status"] != "complete":
                continue

            total_score = result_summary["total_score"]

            if total_score is None:
                continue

            student_results.append(
                {
                    "enrollment_id": class_enrollment.id,
                    "total_score": total_score,
                }
            )

        # --------------------------------
        # SORT HIGHEST FIRST
        # --------------------------------

        student_results.sort(
            key=lambda item: item["total_score"],
            reverse=True,
        )

        # --------------------------------
        # TOTAL COMPLETE STUDENTS
        # --------------------------------

        total_students = len(student_results)

        # --------------------------------
        # FIND STUDENT POSITION
        # --------------------------------

        position = None

        for index, item in enumerate(
            student_results,
            start=1,
        ):

            if (
                item["enrollment_id"]
                == enrollment.id
            ):

                current_score = item["total_score"]

                # Competition ranking:
                # position = number of students
                # with a higher score + 1

                position = (
                    sum(
                        1
                        for student in student_results
                        if student["total_score"]
                        > current_score
                    )
                    + 1
                )

                break

        return {
            "position": (
                cls.format_position(position)
                if position is not None
                else None
            ),

            "total_students": total_students,
        }
    # @classmethod
    # def get_class_position(
    #     cls,
    #     enrollment,
    # ):

    #     # Get all students in the same class,
    #     # academic year and term

    #     class_enrollments = (
    #         Enrollment.objects
    #         .filter(
    #             academic_year=enrollment.academic_year,
    #             term=enrollment.term,
    #             school_class=enrollment.school_class,
    #             is_current=True,
    #             student__status="active",
    #         )
    #     )

    #     student_results = []

    #     # Calculate total score for each student

    #     for class_enrollment in class_enrollments:

    #         result_summary = (
    #             cls.get_student_result_summary(
    #                 class_enrollment
    #             )
    #         )

            
    #         total_score = (
    #             result_summary[
    #                 "total_score"
    #             ]
    #         )

    #         scored_subject_count = (
    #             result_summary[
    #                 "scored_subject_count"
    #             ]
    #         )

    #         if scored_subject_count > 0:

    #             student_results.append(
    #                 {
    #                     "enrollment_id": (
    #                         class_enrollment.id
    #                     ),
    #                     "total_score": total_score,
    #                 }
    #             )

    #     # Order students from highest score

    #     student_results.sort(
    #         key=lambda item: item["total_score"],
    #         reverse=True,
    #     )

    #     # Total students with results

    #     total_students = len(
    #         student_results
    #     )

    #     # IMPORTANT:
    #     # Define position before formatting it

    #     position = None

    #     for index, item in enumerate(
    #         student_results,
    #         start=1,
    #     ):

    #         if (
    #             item["enrollment_id"]
    #             == enrollment.id
    #         ):

    #             position = index

    #             break

    #     return {
    #         "position": (
    #             cls.format_position(position)
    #             if position is not None
    #             else None
    #         ),
    #         "total_students": total_students,
    #     }
    # --------------------------------
    # RESULT ATTENDANCE SUMMARY
    # --------------------------------

    @staticmethod
    def get_result_attendance_summary(enrollment):

        records = Attendance.objects.filter(
            student=enrollment.student,
            attendance_date__gte=enrollment.term.start_date,
            attendance_date__lte=enrollment.term.end_date,
        )

        total = records.count()

        present = records.filter(
            status="present"
        ).count()

        absent = records.filter(
            status="absent"
        ).count()

        late = records.filter(
            status="late"
        ).count()

        excused = records.filter(
            status="excused"
        ).count()

        attendance_rate = 0

        if total:

            attendance_rate = round(
                (present / total) * 100,
                2,
            )

        return {
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
            "attendance_rate": attendance_rate,
        }
    

    # --------------------------------
    # COMPLETE STUDENT REPORT
    # --------------------------------

    @classmethod
    def get_complete_student_result(
        cls,
        enrollment,
    ):

        # --------------------------------
        # RESULT SUMMARY
        # --------------------------------

        result_summary = (
            cls.get_student_result_summary(
                enrollment
            )
        )

        # --------------------------------
        # ASSESSMENT COMPONENTS
        # --------------------------------

        assessment_components = (
            AssessmentComponent.objects
            .filter(
                term=enrollment.term,
                is_active=True,
            )
            .order_by(
                "order",
                "name",
            )
        )

        # --------------------------------
        # SUBJECT RESULTS
        # --------------------------------

        subject_results = (
            StudentSubjectResult.objects
            .filter(
                enrollment=enrollment,
            )
            .select_related(
                "class_subject",
                "class_subject__subject",
            )
            .prefetch_related(
                "assessment_scores",
                "assessment_scores__assessment_component",
            )
            .order_by(
                "class_subject__subject__name",
            )
        )

        # --------------------------------
        # MAP SCORES TO COMPONENTS
        # --------------------------------

        report_subject_results = []

        for subject_result in subject_results:

            score_map = {}

            for assessment_score in (
                subject_result
                .assessment_scores
                .all()
            ):

                score_map[
                    assessment_score
                    .assessment_component_id
                ] = assessment_score.score

            report_subject_results.append(
                {
                    "result": subject_result,
                    "scores": score_map,
                }
            )

        # --------------------------------
        # POSITION
        # --------------------------------

        position_data = (
            cls.get_class_position(
                enrollment
            )
        )

        # --------------------------------
        # ATTENDANCE
        # --------------------------------

        attendance_data = (
            cls.get_result_attendance_summary(
                enrollment
            )
        )

        # --------------------------------
        # BEHAVIOUR
        # --------------------------------

        behaviour_ratings = (
            cls.get_student_behaviour_ratings(
                enrollment
            )
        )

        term_report, created = (
            StudentTermReport.objects.get_or_create(
                enrollment=enrollment
            )
        )

        # --------------------------------
        # FINAL REPORT DATA
        # --------------------------------

        return {

            "enrollment": enrollment,

            "student": enrollment.student,
            "term_report": term_report,

            "assessment_components": (
                assessment_components
            ),

            "subject_results": (
                report_subject_results
            ),

            "total_score": (
                result_summary[
                    "total_score"
                ]
            ),

            "scored_subject_count": (
                result_summary[
                    "scored_subject_count"
                ]
            ),

            "average_score": (
                result_summary[
                    "average_score"
                ]
            ),

            "position": (
                position_data[
                    "position"
                ]
            ),
            

            "total_students": (
                position_data[
                    "total_students"
                ]
            ),

            "attendance": attendance_data,

            "behaviour_ratings": (
                behaviour_ratings
            ),
            "status": result_summary["status"],
        }

    # --------------------------------
    # FORMAT POSITION
    # --------------------------------

    @staticmethod
    def format_position(position):

        if 10 <= position % 100 <= 20:

            suffix = "th"

        else:

            suffix_map = {
                1: "st",
                2: "nd",
                3: "rd",
            }

            suffix = suffix_map.get(
                position % 10,
                "th",
            )

        return f"{position}{suffix}"