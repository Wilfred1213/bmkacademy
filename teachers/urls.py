from django.urls import path

from . import views


app_name = "teachers"


urlpatterns = [

    # Teacher management
    path(
        "",
        views.teacher_list,
        name="teacher_list",
    ),

    path(
        "create/",
        views.create_teacher,
        name="create_teacher",
    ),

    path(
        "<int:teacher_id>/",
        views.teacher_detail,
        name="teacher_detail",
    ),

    path(
        "<int:teacher_id>/edit/",
        views.update_teacher,
        name="update_teacher",
    ),

    # Subject teacher assignments
    path(
        "teaching-assignments/",
        views.teaching_assignment_list,
        name="teaching_assignment_list",
    ),

    path(
        "teaching-assignments/create/",
        views.assign_subject_teacher,
        name="assign_subject_teacher",
    ),

    # Class teacher assignments
    path(
        "class-teachers/",
        views.class_teacher_assignment_list,
        name="class_teacher_assignment_list",
    ),

    path(
        "class-teachers/create/",
        views.assign_class_teacher,
        name="assign_class_teacher",
    ),

]