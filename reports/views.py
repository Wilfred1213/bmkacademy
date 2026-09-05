from django.shortcuts import get_object_or_404, render

from academics.models import AcademicYear, Term, SchoolClass
from students.models import Enrollment

from .services import ReportService


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

    report = ReportService.get_student_term_report(
        enrollment
    )

    return render(
        request,
        "reports/student_report.html",
        {
            "report": report,
        },
    )

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

    class_results = ReportService.get_class_performance(
        academic_year=academic_year,
        term=term,
        school_class=school_class,
    )

    # =========================
    # CLASS STATISTICS
    # =========================

    averages = [
        result["average"]
        for result in class_results
        if result["average"] is not None
    ]

    class_average = (
        sum(averages) / len(averages)
        if averages
        else 0
    )

    highest_average = (
        max(averages)
        if averages
        else 0
    )

    lowest_average = (
        min(averages)
        if averages
        else 0
    )

    context = {
        "academic_year": academic_year,
        "term": term,
        "school_class": school_class,
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
# def class_performance_report(request, academic_year_id, term_id, school_class_id):

#     academic_year = get_object_or_404(
#         AcademicYear,
#         id=academic_year_id,
#     )

#     term = get_object_or_404(
#         Term,
#         id=term_id,
#         academic_year=academic_year,
#     )

#     school_class = get_object_or_404(
#         SchoolClass,
#         id=school_class_id,
#     )

#     class_results = ReportService.get_class_performance(
#         academic_year=academic_year,
#         term=term,
#         school_class=school_class,
#     )

#     return render(
#         request,
#         "reports/class_performance_report.html",
#         {
#             "academic_year": academic_year,
#             "term": term,
#             "school_class": school_class,
#             "class_results": class_results,
#         },
#     )