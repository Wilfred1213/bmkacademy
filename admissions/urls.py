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
    path(
    "parent-applications/<int:application_id>/",
    views.parent_admission_detail,
    name="parent_admission_detail",
    ),
    path(
    "claim/<uuid:claim_token>/",
    views.claim_application,
    name="claim_application",
    ),
    path(
    "applications/<int:application_id>/resend-email/",
    views.resend_admission_email,
    name="resend_admission_email",
    ),
    path(
    "applications/<int:application_id>/regenerate-claim/",
    views.regenerate_claim_token,
    name="regenerate_claim_token",
),

]