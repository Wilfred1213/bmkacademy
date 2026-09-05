from django.urls import path

from . import views


app_name = "reports"


urlpatterns = [
    path(
        "",
        views.report_dashboard,
        name="report_dashboard",
    ),

    path(
        "student/<int:enrollment_id>/",
        views.student_report,
        name="student_report",
    ),
    path(
    "class-performance/<int:academic_year_id>/<int:term_id>/<int:school_class_id>/",
    views.class_performance_report,
    name="class_performance_report",
),
    

]