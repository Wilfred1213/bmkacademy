from django.urls import path

from . import views


app_name = "admissions"


urlpatterns = [

    path(
        "terms/",
        views.admission_terms,
        name="admission_terms",
    ),
    path(
        "admission/",
        views.admission_application,
        name="admission_application",
    ),
    path(
    "applications/",
    views.admission_list,
    name="admission_list",
    ),
    path(
    "applications/<int:application_id>/",
    views.admission_detail,
    name="admission_detail",
    ),
    path(
    "applications/<int:application_id>/approve/",
    views.approve_application,
    name="approve_application",
    ),
    path(
    "applications/<int:application_id>/reject/",
    views.reject_application,
    name="reject_application",
),

]