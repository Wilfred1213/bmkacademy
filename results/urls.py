from django.urls import path

from . import views


app_name = "results"


urlpatterns = [

    path(
        "enter/",
        views.enter_results,
        name="enter_results",
    ),

    path(
    "student/<int:enrollment_id>/",
    views.student_result,
    name="student_result",
    ),
    path(
    "behaviour/enter/",
    views.enter_behaviour_ratings,
    name="enter_behaviour_ratings",
    ),
    path(
    "student-report/<int:enrollment_id>/",
    views.student_report_card,
    name="student_report_card",
    ),
    path(
    "report-remarks/",
    views.enter_report_remarks,
    name="enter_report_remarks",
    ),
    path(
    "student-report/<int:enrollment_id>/toggle-publication/",
    views.toggle_report_publication,
    name="toggle_report_publication",
),

]