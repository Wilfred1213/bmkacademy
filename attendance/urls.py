from django.urls import path

from . import views


app_name = "attendance"

urlpatterns = [
    path(
        "mark/",
        views.mark_attendance,
        name="mark_attendance",
    ),
    path(
    "history/",
    views.attendance_history,
    name="attendance_history",
    
    ),
    path(
    "student/<int:student_id>/",
    views.student_attendance,
    name="student_attendance",
),

    
]