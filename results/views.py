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
from django.db import transaction

from .models import (
    AssessmentComponent,
    StudentSubjectResult,
    BehaviourCategory,
    StudentBehaviourRating,
    StudentTermReport
)

from .services import ResultService
from django.urls import reverse




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

def enter_behaviour_ratings(request):

    academic_years = AcademicYear.objects.order_by(
        "-start_date"
    )

    school_classes = SchoolClass.objects.order_by(
        "section",
        "name",
    )

    behaviour_categories = (
        BehaviourCategory.objects
        .filter(
            is_active=True,
        )
        .order_by(
            "order",
            "name",
        )
    )

    selected_academic_year = None
    selected_term = None
    selected_class = None
    selected_enrollment = None

    terms = []
    students = []

    existing_ratings = {}

    # --------------------------------
    # GET
    # --------------------------------

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

        enrollment_id = request.GET.get(
            "enrollment"
        )

        # --------------------------------
        # ACADEMIC YEAR
        # --------------------------------

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
                    academic_year=selected_academic_year,
                )
                .order_by(
                    "start_date"
                )
            )

        # --------------------------------
        # TERM
        # --------------------------------

        if term_id and selected_academic_year:

            selected_term = (
                get_object_or_404(
                    Term,
                    id=term_id,
                    academic_year=selected_academic_year,
                )
            )

        # --------------------------------
        # CLASS
        # --------------------------------

        if school_class_id:

            selected_class = (
                get_object_or_404(
                    SchoolClass,
                    id=school_class_id,
                )
            )

        # --------------------------------
        # LOAD STUDENTS
        # --------------------------------

        if (
            selected_academic_year
            and selected_term
            and selected_class
        ):

            students = (
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

        # --------------------------------
        # SELECT STUDENT
        # --------------------------------

        if (
            enrollment_id
            and selected_academic_year
            and selected_term
            and selected_class
        ):

            selected_enrollment = (
                get_object_or_404(
                    Enrollment.objects.select_related(
                        "student"
                    ),
                    id=enrollment_id,
                    academic_year=selected_academic_year,
                    term=selected_term,
                    school_class=selected_class,
                    is_current=True,
                    student__status="active",
                )
            )

            existing_ratings = {

                rating.behaviour_category_id:
                rating.rating

                for rating in (
                    ResultService
                    .get_student_behaviour_ratings(
                        enrollment=selected_enrollment
                    )
                )
            }

    # --------------------------------
    # POST
    # --------------------------------

    elif request.method == "POST":

        with transaction.atomic():

            selected_academic_year = (
                get_object_or_404(
                    AcademicYear,
                    id=request.POST[
                        "academic_year"
                    ],
                )
            )

            selected_term = (
                get_object_or_404(
                    Term,
                    id=request.POST[
                        "term"
                    ],
                    academic_year=selected_academic_year,
                )
            )

            selected_class = (
                get_object_or_404(
                    SchoolClass,
                    id=request.POST[
                        "school_class"
                    ],
                )
            )

            selected_enrollment = (
                get_object_or_404(
                    Enrollment,
                    id=request.POST[
                        "enrollment"
                    ],
                    academic_year=selected_academic_year,
                    term=selected_term,
                    school_class=selected_class,
                    is_current=True,
                    student__status="active",
                )
            )

            rating_data = {}

            for category in behaviour_categories:

                rating = request.POST.get(
                    f"rating_{category.id}"
                )

                if rating:

                    rating_data[
                        category.id
                    ] = rating

            ResultService.save_behaviour_ratings(
                enrollment=selected_enrollment,
                rating_data=rating_data,
            )

        messages.success(
            request,
            "Behaviour ratings saved successfully."
        )

        url = (
            reverse(
                "results:enter_behaviour_ratings"
            )
            + f"?academic_year={selected_academic_year.id}"
            + f"&term={selected_term.id}"
            + f"&school_class={selected_class.id}"
            + f"&enrollment={selected_enrollment.id}"
        )

        return redirect(url)

    # --------------------------------
    # FINAL RESPONSE
    # --------------------------------

    return render(
        request,
        "results/enter_behaviour_ratings.html",
        {
            "academic_years": academic_years,
            "school_classes": school_classes,
            "terms": terms,
            "students": students,
            "behaviour_categories": (
                behaviour_categories
            ),
            "selected_academic_year": (
                selected_academic_year
            ),
            "selected_term": selected_term,
            "selected_class": selected_class,
            "selected_enrollment": (
                selected_enrollment
            ),
            "existing_ratings": (
                existing_ratings
            ),
        },
    )

# --------------------------------
# STUDENT REPORT CARD
# --------------------------------

def student_report_card(
    request,
    enrollment_id,
):

    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            "student",
            "academic_year",
            "term",
            "school_class",
        ),
        id=enrollment_id,
    )

    report = (
        ResultService
        .get_complete_student_result(
            enrollment=enrollment
        )
    )

    return render(
        request,
        "results/student_report_card.html",
        {
            "report": report,
        },
    )

def enter_report_remarks(request):

    academic_years = AcademicYear.objects.order_by(
        "-start_date"
    )

    school_classes = SchoolClass.objects.order_by(
        "section",
        "name",
    )

    selected_academic_year = None
    selected_term = None
    selected_class = None
    selected_enrollment = None

    terms = []
    students = []

    # --------------------------------
    # GET
    # --------------------------------

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

        enrollment_id = request.GET.get(
            "enrollment"
        )

        # Academic Year
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

        # Term
        if term_id and selected_academic_year:

            selected_term = (
                get_object_or_404(
                    Term,
                    id=term_id,
                    academic_year=selected_academic_year,
                )
            )

        # School Class
        if school_class_id:

            selected_class = (
                get_object_or_404(
                    SchoolClass,
                    id=school_class_id,
                )
            )

        # Students
        if (
            selected_academic_year
            and selected_term
            and selected_class
        ):

            students = (
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

        # Selected Student
        if (
            enrollment_id
            and selected_academic_year
            and selected_term
            and selected_class
        ):

            selected_enrollment = (
                get_object_or_404(
                    Enrollment.objects.select_related(
                        "student"
                    ),
                    id=enrollment_id,
                    academic_year=selected_academic_year,
                    term=selected_term,
                    school_class=selected_class,
                    is_current=True,
                    student__status="active",
                )
            )

    # --------------------------------
    # POST
    # --------------------------------

    elif request.method == "POST":

        selected_academic_year = (
            get_object_or_404(
                AcademicYear,
                id=request.POST[
                    "academic_year"
                ],
            )
        )

        selected_term = (
            get_object_or_404(
                Term,
                id=request.POST[
                    "term"
                ],
                academic_year=selected_academic_year,
            )
        )

        selected_class = (
            get_object_or_404(
                SchoolClass,
                id=request.POST[
                    "school_class"
                ],
            )
        )

        selected_enrollment = (
            get_object_or_404(
                Enrollment,
                id=request.POST[
                    "enrollment"
                ],
                academic_year=selected_academic_year,
                term=selected_term,
                school_class=selected_class,
                is_current=True,
                student__status="active",
            )
        )

        report, created = (
            StudentTermReport.objects
            .get_or_create(
                enrollment=selected_enrollment
            )
        )

        report.teacher_remark = request.POST.get(
            "teacher_remark",
            ""
        )

        report.head_teacher_remark = request.POST.get(
            "head_teacher_remark",
            ""
        )

        report.next_term_begins = (
            request.POST.get(
                "next_term_begins"
            )
            or None
        )

        report.save()

        messages.success(
            request,
            "Report remarks saved successfully."
        )

        return redirect(
            f"{request.path}"
            f"?academic_year="
            f"{selected_academic_year.id}"
            f"&term={selected_term.id}"
            f"&school_class="
            f"{selected_class.id}"
            f"&enrollment="
            f"{selected_enrollment.id}"
        )

    # --------------------------------
    # EXISTING REPORT
    # --------------------------------

    existing_report = None

    if selected_enrollment:

        existing_report = (
            StudentTermReport.objects
            .filter(
                enrollment=selected_enrollment
            )
            .first()
        )

    # --------------------------------
    # FINAL RESPONSE
    # --------------------------------

    return render(
        request,
        "results/enter_report_remarks.html",
        {
            "academic_years": academic_years,
            "school_classes": school_classes,
            "terms": terms,
            "students": students,
            "selected_academic_year": (
                selected_academic_year
            ),
            "selected_term": selected_term,
            "selected_class": selected_class,
            "selected_enrollment": (
                selected_enrollment
            ),
            "existing_report": existing_report,
        },
    )


def toggle_report_publication(
    request,
    enrollment_id,
):

    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            "student",
            "academic_year",
            "term",
            "school_class",
        ),
        id=enrollment_id,
    )

    report, created = (
        StudentTermReport.objects
        .get_or_create(
            enrollment=enrollment
        )
    )

    if request.method == "POST":

        # Check whether the student's result is complete
        result_status = (
            ResultService
            .get_student_result_status(
                enrollment
            )
        )

        # Do not allow an incomplete result
        # to be published
        if (
            not result_status["is_complete"]
            and not report.is_published
        ):
            messages.error(
                request,
                "This result cannot be published because "
                "some required assessments are still missing."
            )

            return redirect(
                "results:student_report_card",
                enrollment_id=enrollment.id,
            )

        # Toggle publication
        report.is_published = (
            not report.is_published
        )

        report.save(
            update_fields=[
                "is_published",
                "updated_at",
            ]
        )

        if report.is_published:

            messages.success(
                request,
                "Report published successfully."
            )

        else:

            messages.warning(
                request,
                "Report has been unpublished."
            )

    return redirect(
        "results:student_report_card",
        enrollment_id=enrollment.id,
    )
