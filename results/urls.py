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

]