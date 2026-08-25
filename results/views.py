from django.contrib import messages

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from academics.models import (
    AcademicYear,
    ClassSubject,
    SchoolClass,
    Term,
)

from students.models import Enrollment

from .models import (
    AssessmentComponent,
    StudentSubjectResult,
)

from .services import ResultService


def enter_results(request):

    academic_years = (
        AcademicYear.objects
        .order_by("-start_date")
    )

    school_classes = (
        SchoolClass.objects
        .order_by(
            "section",
            "name",
        )
    )

    selected_academic_year = None
    selected_term = None
    selected_class = None
    selected_class_subject = None

    terms = []
    class_subjects = []
    students = []
    assessment_components = []

    # =================================
    # GET
    # =================================

    if request.method == "GET":

        academic_year_id = request.GET.get(
            "academic_year"
        )

        term_id = request.GET.get(
            "term"
        )

        school_class_id = request.GET.get(
            "school_class"
        )

        class_subject_id = request.GET.get(
            "class_subject"
        )

        # -------------------------------
        # Academic Year
        # -------------------------------

        if academic_year_id:

            selected_academic_year = (
                get_object_or_404(
                    AcademicYear,
                    id=academic_year_id,
                )
            )

            terms = (
                Term.objects
                .filter(
                    academic_year=selected_academic_year
                )
                .order_by(
                    "start_date"
                )
            )

        # -------------------------------
        # Term
        # -------------------------------

        if (
            term_id
            and selected_academic_year
        ):

            selected_term = (
                get_object_or_404(
                    Term,
                    id=term_id,
                    academic_year=selected_academic_year,
                )
            )

        # -------------------------------
        # School Class
        # -------------------------------

        if school_class_id:

            selected_class = (
                get_object_or_404(
                    SchoolClass,
                    id=school_class_id,
                )
            )

            class_subjects = (
                ClassSubject.objects
                .select_related(
                    "subject"
                )
                .filter(
                    school_class=selected_class,
                    is_active=True,
                )
                .order_by(
                    "subject__name"
                )
            )

        # -------------------------------
        # Class Subject
        # -------------------------------

        if (
            class_subject_id
            and selected_class
        ):

            selected_class_subject = (
                ClassSubject.objects
                .filter(
                    id=class_subject_id,
                    school_class=selected_class,
                    is_active=True,
                )
                .first()
            )

        # -------------------------------
        # Load Students
        # -------------------------------

        if (
            selected_academic_year
            and selected_term
            and selected_class
            and selected_class_subject
        ):

            students = list(
                Enrollment.objects
                .filter(
                    academic_year=selected_academic_year,
                    term=selected_term,
                    school_class=selected_class,
                    is_current=True,
                    student__status="active",
                )
                .select_related(
                    "student"
                )
                .order_by(
                    "student__first_name",
                    "student__last_name",
                )
            )

            # ---------------------------
            # Assessment Components
            # ---------------------------

            assessment_components = list(
                AssessmentComponent.objects
                .filter(
                    term=selected_term,
                    is_active=True,
                )
                .order_by(
                    "order",
                    "name",
                )
            )

            # ---------------------------
            # Existing Results
            # ---------------------------

            results = (
                StudentSubjectResult.objects
                .filter(
                    enrollment__in=students,
                    class_subject=selected_class_subject,
                )
                .prefetch_related(
                    "assessment_scores"
                )
            )

            existing_results = {}

            for result in results:

                scores = {}

                for score in (
                    result.assessment_scores.all()
                ):

                    scores[
                        score.assessment_component_id
                    ] = score.score

                existing_results[
                    result.enrollment_id
                ] = scores

            # ---------------------------
            # Attach Scores to Enrollment
            # ---------------------------

            for enrollment in students:

                scores = existing_results.get(
                    enrollment.id,
                    {}
                )

                enrollment.result_scores = []

                for component in assessment_components:

                    enrollment.result_scores.append(
                        {
                            "component": component,
                            "score": scores.get(
                                component.id
                            ),
                        }
                    )
    # =================================
    # POST
    # =================================

    elif request.method == "POST":

        selected_academic_year = (
            get_object_or_404(
                AcademicYear,
                id=request.POST["academic_year"],
            )
        )

        selected_term = get_object_or_404(
            Term,
            id=request.POST["term"],
            academic_year=selected_academic_year,
        )

        selected_class = get_object_or_404(
            SchoolClass,
            id=request.POST["school_class"],
        )

        selected_class_subject = (
            get_object_or_404(
                ClassSubject,
                id=request.POST["class_subject"],
                school_class=selected_class,
                is_active=True,
            )
        )

        # -------------------------------
        # Save Results
        # -------------------------------

        ResultService.save_class_results(
            academic_year=selected_academic_year,
            term=selected_term,
            school_class=selected_class,
            class_subject=selected_class_subject,
            result_data=request.POST,
        )

        messages.success(
            request,
            "Results saved successfully.",
        )

        return redirect(
            "results:enter_results"
        )

    # =================================
    # FINAL RESPONSE
    # =================================

    return render(
        request,
        "results/enter_results.html",
        {
            "academic_years": academic_years,
            "school_classes": school_classes,
            "terms": terms,
            "class_subjects": class_subjects,
            "students": students,
            "assessment_components": (
                assessment_components
            ),
            "selected_academic_year": (
                selected_academic_year
            ),
            "selected_term": (
                selected_term
            ),
            "selected_class": (
                selected_class
            ),
            "selected_class_subject": (
                selected_class_subject
            ),
        },
    )

def student_result(
    request,
    enrollment_id,
    ):

    enrollment = get_object_or_404(
        Enrollment.objects
        .select_related(
            "student",
            "academic_year",
            "term",
            "school_class",
        ),
        id=enrollment_id,
    )

    result_summary = (
        ResultService.get_student_term_result(
            enrollment=enrollment
        )
    )

    return render(
        request,
        "results/student_result.html",
        {
            "enrollment": enrollment,
            "result_summary": result_summary,
        },
    )