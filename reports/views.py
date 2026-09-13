from django.shortcuts import get_object_or_404,redirect, render

from academics.models import AcademicYear, Term, SchoolClass
from students.models import Enrollment
from decimal import Decimal
from .services import ReportService

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from accounts.decorators import role_required

from teachers.models import Teacher, ClassTeacherAssignment

@login_required
@role_required("admin", "teacher")
def report_dashboard(request):

    academic_years = AcademicYear.objects.all()

    terms = Term.objects.none()
    classes = SchoolClass.objects.none()
    enrollments = Enrollment.objects.none()

    academic_year_id = request.GET.get("academic_year")
    term_id = request.GET.get("term")
    class_id = request.GET.get("school_class")

    if academic_year_id:

        terms = Term.objects.filter(
            academic_year_id=academic_year_id
        ).order_by("start_date")

    if term_id:

        classes = SchoolClass.objects.filter(
            enrollments__term_id=term_id
        ).distinct().order_by("name")

    if term_id and class_id:

        enrollments = (
            Enrollment.objects
            .select_related(
                "student",
                "academic_year",
                "term",
                "school_class",
            )
            .filter(
                academic_year_id=academic_year_id,
                term_id=term_id,
                school_class_id=class_id,
            )
            .order_by(
                "student__first_name",
                "student__last_name",
            )
        )

    return render(
        request,
        "reports/report_dashboard.html",
        {
            "academic_years": academic_years,
            "terms": terms,
            "classes": classes,
            "enrollments": enrollments,

            "selected_academic_year": academic_year_id,
            "selected_term": term_id,
            "selected_class": class_id,
        },
    )


@login_required
@role_required("admin", "teacher")
def student_report(request, enrollment_id):

    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            "student",
            "academic_year",
            "term",
            "school_class",
        ),
        id=enrollment_id,
    )

    return redirect(
        "results:student_report_card",
        enrollment_id=enrollment.id,
    )

@login_required
@role_required("admin", "teacher")
def class_performance_report(
request,
academic_year_id,
term_id,
school_class_id,
):
    academic_year = get_object_or_404(
    AcademicYear,
    id=academic_year_id,
    )

    term = get_object_or_404(
        Term,
        id=term_id,
        academic_year=academic_year,
    )

    school_class = get_object_or_404(
        SchoolClass,
        id=school_class_id,
    )

    # -----------------------------------------
    # TEACHER PERMISSION CHECK
    # -----------------------------------------
    if request.user.role == "teacher":

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
            is_active=True,
        )

        is_class_teacher = (
            ClassTeacherAssignment.objects.filter(
                teacher=teacher,
                school_class=school_class,
                academic_year=academic_year,
                is_active=True,
            ).exists()
        )

        if not is_class_teacher:
            raise PermissionDenied

    # -----------------------------------------
    # GET CLASS RESULTS
    # -----------------------------------------
    performance = ReportService.get_class_performance(
        academic_year=academic_year,
        term=term,
        school_class=school_class,
    )

    subjects = performance["subjects"]
    class_results = performance["class_results"]

    # -----------------------------------------
    # CLASS STATISTICS
    # -----------------------------------------
    averages = [
        Decimal(str(result["average"]))
        for result in class_results
        if result["average"] is not None
    ]

    class_average = (
        sum(
            averages,
            Decimal("0"),
        )
        / Decimal(len(averages))
        if averages
        else Decimal("0")
    )

    highest_average = (
        max(averages)
        if averages
        else Decimal("0")
    )

    lowest_average = (
        min(averages)
        if averages
        else Decimal("0")
    )

    context = {
        "academic_year": academic_year,
        "term": term,
        "school_class": school_class,
        "subjects": subjects,
        "class_results": class_results,
        "class_average": class_average,
        "highest_average": highest_average,
        "lowest_average": lowest_average,
        "student_count": len(class_results),
    }

    return render(
        request,
        "reports/class_performance_report.html",
        context,
    )

