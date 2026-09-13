from django.contrib import messages
from django.core.exceptions import PermissionDenied
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
from django.contrib.auth.decorators import login_required

from accounts.decorators import role_required
from teachers.models import (
    Teacher,
    TeachingAssignment,
    ClassTeacherAssignment,
)
from django.db.models import Q



@login_required
@role_required("admin", "teacher")
def enter_results(request):

    academic_years = (
        AcademicYear.objects
        .order_by("-start_date")
    )

    if request.user.role == "admin":

        school_classes = (
            SchoolClass.objects
            .order_by(
                "section",
                "name",
            )
        )

    else:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
            is_active=True,
        )

        class_teacher_classes = (
            ClassTeacherAssignment.objects
            .filter(
                teacher=teacher,
                is_active=True,
            )
            .values_list(
                "school_class_id",
                flat=True,
            )
        )

        subject_teacher_classes = (
            TeachingAssignment.objects
            .filter(
                teacher=teacher,
                is_active=True,
            )
            .values_list(
                "class_subject__school_class_id",
                flat=True,
            )
        )

        school_classes = (
            SchoolClass.objects
            .filter(
                Q(id__in=class_teacher_classes)
                | Q(id__in=subject_teacher_classes)
            )
            .distinct()
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

            selected_class = get_object_or_404(
                school_classes,
                id=school_class_id,
            )

            if request.user.role == "admin":

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

            else:

                teacher = get_object_or_404(
                    Teacher,
                    user=request.user,
                    is_active=True,
                )

                is_class_teacher = (
                    ClassTeacherAssignment.objects
                    .filter(
                        teacher=teacher,
                        school_class=selected_class,
                        academic_year=selected_academic_year,
                        is_active=True,
                    )
                    .exists()
                )

                if is_class_teacher:

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

                else:

                    class_subjects = (
                        ClassSubject.objects
                        .select_related(
                            "subject"
                        )
                        .filter(
                            school_class=selected_class,
                            is_active=True,
                            teaching_assignments__teacher=teacher,
                            teaching_assignments__academic_year=selected_academic_year,
                            teaching_assignments__is_active=True,
                        )
                        .distinct()
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

            if request.user.role == "admin":

                selected_class_subject = (
                    ClassSubject.objects
                    .filter(
                        id=class_subject_id,
                        school_class=selected_class,
                        is_active=True,
                    )
                    .first()
                )

            else:

                teacher = get_object_or_404(
                    Teacher,
                    user=request.user,
                    is_active=True,
                )

                is_class_teacher = (
                    ClassTeacherAssignment.objects
                    .filter(
                        teacher=teacher,
                        school_class=selected_class,
                        academic_year=selected_academic_year,
                        is_active=True,
                    )
                    .exists()
                )

                if is_class_teacher:

                    selected_class_subject = (
                        ClassSubject.objects
                        .filter(
                            id=class_subject_id,
                            school_class=selected_class,
                            is_active=True,
                        )
                        .first()
                    )

                else:

                    selected_class_subject = (
                        ClassSubject.objects
                        .filter(
                            id=class_subject_id,
                            school_class=selected_class,
                            is_active=True,
                            teaching_assignments__teacher=teacher,
                            teaching_assignments__academic_year=selected_academic_year,
                            teaching_assignments__is_active=True,
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
            school_classes,
            id=request.POST["school_class"],
        )

        if request.user.role == "admin":

            selected_class_subject = get_object_or_404(
                ClassSubject,
                id=request.POST["class_subject"],
                school_class=selected_class,
                is_active=True,
            )

        else:

            teacher = get_object_or_404(
                Teacher,
                user=request.user,
                is_active=True,
            )

            is_class_teacher = (
                ClassTeacherAssignment.objects
                .filter(
                    teacher=teacher,
                    school_class=selected_class,
                    academic_year=selected_academic_year,
                    is_active=True,
                )
                .exists()
            )

            if is_class_teacher:

                selected_class_subject = get_object_or_404(
                    ClassSubject,
                    id=request.POST["class_subject"],
                    school_class=selected_class,
                    is_active=True,
                )

            else:

                selected_class_subject = get_object_or_404(
                    ClassSubject,
                    id=request.POST["class_subject"],
                    school_class=selected_class,
                    is_active=True,
                    teaching_assignments__teacher=teacher,
                    teaching_assignments__academic_year=selected_academic_year,
                    teaching_assignments__is_active=True,
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



@login_required
@role_required("admin", "teacher")
def student_result(
    request,
    enrollment_id,
):

    # =================================
    # GET ENROLLMENT
    # =================================

    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            "student",
            "academic_year",
            "term",
            "school_class",
        ),
        id=enrollment_id,
    )

    # =================================
    # TEACHER ACCESS
    # =================================

    if request.user.role == "teacher":

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
            is_active=True,
        )

        is_class_teacher = (
            ClassTeacherAssignment.objects.filter(
                teacher=teacher,
                school_class=enrollment.school_class,
                academic_year=enrollment.academic_year,
                is_active=True,
            ).exists()
        )

        if not is_class_teacher:
            raise PermissionDenied

    # =================================
    # GET RESULT
    # =================================

    result_summary = (
        ResultService.get_student_term_result(
            enrollment=enrollment
        )
    )

    # =================================
    # RENDER
    # =================================

    return render(
        request,
        "results/student_result.html",
        {
            "enrollment": enrollment,
            "result_summary": result_summary,
        },
    )

@login_required
@role_required("admin", "teacher")
def enter_behaviour_ratings(request):

    academic_years = AcademicYear.objects.order_by(
        "-start_date"
    )

    selected_academic_year = None
    selected_term = None
    selected_class = None
    selected_enrollment = None

    terms = []
    students = []

    existing_ratings = {}

    # =================================
    # INITIAL SCHOOL CLASSES
    # =================================

    if request.user.role == "admin":

        school_classes = (
            SchoolClass.objects
            .order_by(
                "section",
                "name",
            )
        )

    else:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
            is_active=True,
        )

        # A teacher can only access classes where
        # they are actually assigned as CLASS TEACHER.
        #
        # Subject-teacher assignments are deliberately
        # NOT included here.
        school_classes = (
            SchoolClass.objects
            .filter(
                class_teacher_assignments__teacher=teacher,
                class_teacher_assignments__is_active=True,
            )
            .distinct()
            .order_by(
                "section",
                "name",
            )
        )

    # =================================
    # BEHAVIOUR CATEGORIES
    # =================================

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

        enrollment_id = request.GET.get(
            "enrollment"
        )

        # -------------------------------
        # ACADEMIC YEAR
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
                    academic_year=selected_academic_year,
                )
                .order_by(
                    "start_date"
                )
            )

            # --------------------------------
            # Restrict teacher classes to the
            # selected academic year
            # --------------------------------

            if request.user.role == "teacher":

                teacher = get_object_or_404(
                    Teacher,
                    user=request.user,
                    is_active=True,
                )

                school_classes = (
                    SchoolClass.objects
                    .filter(
                        class_teacher_assignments__teacher=teacher,
                        class_teacher_assignments__academic_year=selected_academic_year,
                        class_teacher_assignments__is_active=True,
                    )
                    .distinct()
                    .order_by(
                        "section",
                        "name",
                    )
                )

        # -------------------------------
        # TERM
        # -------------------------------

        if term_id and selected_academic_year:

            selected_term = (
                get_object_or_404(
                    Term,
                    id=term_id,
                    academic_year=selected_academic_year,
                )
            )

        # -------------------------------
        # CLASS
        # -------------------------------

        if school_class_id:

            selected_class = (
                get_object_or_404(
                    school_classes,
                    id=school_class_id,
                )
            )

        # -------------------------------
        # LOAD STUDENTS
        # -------------------------------

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

        # -------------------------------
        # SELECT STUDENT
        # -------------------------------

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

    # =================================
    # POST
    # =================================

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

            selected_term = get_object_or_404(
                Term,
                id=request.POST[
                    "term"
                ],
                academic_year=selected_academic_year,
            )

            # --------------------------------
            # Restrict class selection
            # --------------------------------

            if request.user.role == "admin":

                selected_class = (
                    get_object_or_404(
                        SchoolClass,
                        id=request.POST[
                            "school_class"
                        ],
                    )
                )

            else:

                teacher = get_object_or_404(
                    Teacher,
                    user=request.user,
                    is_active=True,
                )

                # IMPORTANT:
                # Teacher must be the CLASS TEACHER
                # for this class AND academic year.
                #
                # A subject teacher cannot bypass this
                # restriction by posting a class ID.

                selected_class = (
                    get_object_or_404(
                        SchoolClass,
                        id=request.POST[
                            "school_class"
                        ],
                        class_teacher_assignments__teacher=teacher,
                        class_teacher_assignments__academic_year=selected_academic_year,
                        class_teacher_assignments__is_active=True,
                    )
                )

            # --------------------------------
            # SELECT ENROLLMENT
            # --------------------------------

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

            # --------------------------------
            # COLLECT RATINGS
            # --------------------------------

            rating_data = {}

            for category in behaviour_categories:

                rating = request.POST.get(
                    f"rating_{category.id}"
                )

                if rating:

                    rating_data[
                        category.id
                    ] = rating

            # --------------------------------
            # SAVE RATINGS
            # --------------------------------

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

    # =================================
    # FINAL RESPONSE
    # =================================

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

@login_required
@role_required("admin", "teacher")
def student_report_card(
    request,
    enrollment_id,
):

    # =================================
    # GET ENROLLMENT
    # =================================

    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            "student",
            "academic_year",
            "term",
            "school_class",
        ),
        id=enrollment_id,
    )

    # =================================
    # TEACHER ACCESS
    # =================================

    if request.user.role == "teacher":

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
            is_active=True,
        )

        is_class_teacher = (
            ClassTeacherAssignment.objects.filter(
                teacher=teacher,
                school_class=enrollment.school_class,
                academic_year=enrollment.academic_year,
                is_active=True,
            ).exists()
        )

        if not is_class_teacher:

            raise PermissionDenied

    # =================================
    # POSITION OPTION
    # =================================

    show_position = (
        request.GET.get(
            "show_position"
        ) == "1"
    )

    # ---------------------------------
    # Only admin can request position
    # ---------------------------------

    if request.user.role != "admin":

        show_position = False

    # =================================
    # GET COMPLETE REPORT
    # =================================

    report = (
        ResultService
        .get_complete_student_result(
            enrollment=enrollment,
            include_position=show_position,
        )
    )

    # =================================
    # RENDER
    # =================================

    return render(
        request,
        "results/student_report_card.html",
        {
            "report": report,
        },
    )

@login_required
@role_required("admin", "teacher")
def enter_report_remarks(request):

    academic_years = AcademicYear.objects.order_by(
        "-start_date"
    )

    # =================================
    # SCHOOL CLASSES
    # =================================

    if request.user.role == "admin":

        school_classes = (
            SchoolClass.objects
            .order_by(
                "section",
                "name",
            )
        )

    else:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
            is_active=True,
        )

        school_classes = (
            SchoolClass.objects
            .filter(
                class_teacher_assignments__teacher=teacher,
                class_teacher_assignments__is_active=True,
            )
            .distinct()
            .order_by(
                "section",
                "name",
            )
        )

    selected_academic_year = None
    selected_term = None
    selected_class = None
    selected_enrollment = None

    terms = []
    students = []

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
                    academic_year=selected_academic_year
                )
                .order_by(
                    "start_date"
                )
            )

            # Teacher can only see classes where
            # they are the class teacher for the
            # selected academic year.
            if request.user.role == "teacher":

                teacher = get_object_or_404(
                    Teacher,
                    user=request.user,
                    is_active=True,
                )

                school_classes = (
                    SchoolClass.objects
                    .filter(
                        class_teacher_assignments__teacher=teacher,
                        class_teacher_assignments__academic_year=selected_academic_year,
                        class_teacher_assignments__is_active=True,
                    )
                    .distinct()
                    .order_by(
                        "section",
                        "name",
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
        # SCHOOL CLASS
        # --------------------------------

        if school_class_id:

            selected_class = get_object_or_404(
                school_classes,
                id=school_class_id,
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

    # =================================
    # POST
    # =================================

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

        # --------------------------------
        # CLASS ACCESS
        # --------------------------------

        if request.user.role == "admin":

            selected_class = get_object_or_404(
                SchoolClass,
                id=request.POST[
                    "school_class"
                ],
            )

        else:

            teacher = get_object_or_404(
                Teacher,
                user=request.user,
                is_active=True,
            )

            # A teacher MUST be the class teacher
            # for this class AND academic year.
            selected_class = (
                get_object_or_404(
                    SchoolClass,
                    id=request.POST[
                        "school_class"
                    ],
                    class_teacher_assignments__teacher=teacher,
                    class_teacher_assignments__academic_year=selected_academic_year,
                    class_teacher_assignments__is_active=True,
                )
            )

        # --------------------------------
        # SELECT ENROLLMENT
        # --------------------------------

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

        # --------------------------------
        # GET OR CREATE REPORT
        # --------------------------------

        report, created = (
            StudentTermReport.objects
            .get_or_create(
                enrollment=selected_enrollment
            )
        )

        # --------------------------------
        # CLASS TEACHER REMARK
        # --------------------------------

        report.teacher_remark = request.POST.get(
            "teacher_remark",
            ""
        )

        # --------------------------------
        # HEAD TEACHER REMARK
        # --------------------------------
        #
        # ONLY ADMIN can modify this field.
        #
        # Even if a teacher manually adds
        # "head_teacher_remark" to the POST request,
        # it will be completely ignored.

        if request.user.role == "admin":

            report.head_teacher_remark = (
                request.POST.get(
                    "head_teacher_remark",
                    ""
                )
            )

        # --------------------------------
        # NEXT TERM DATE
        # --------------------------------

        if request.user.role == "admin":

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

    # =================================
    # EXISTING REPORT
    # =================================

    existing_report = None

    if selected_enrollment:

        existing_report = (
            StudentTermReport.objects
            .filter(
                enrollment=selected_enrollment
            )
            .first()
        )

    # =================================
    # FINAL RESPONSE
    # =================================

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



@login_required
@role_required("admin")
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

        # =================================
        # CHECK RESULT COMPLETION
        # =================================

        result_status = (
            ResultService
            .get_student_result_status(
                enrollment
            )
        )

        # =================================
        # DO NOT PUBLISH INCOMPLETE RESULT
        # =================================

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

        # =================================
        # TOGGLE PUBLICATION
        # =================================

        report.is_published = (
            not report.is_published
        )

        report.save(
            update_fields=[
                "is_published",
                "updated_at",
            ]
        )

        # =================================
        # MESSAGE
        # =================================

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