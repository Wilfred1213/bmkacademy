from django.urls import path

from . import views


app_name = "admissions"


urlpatterns = [

    # path(
    #     "apply/",
    #     views.apply_admission,
    #     name="apply_admission",
    # ),
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

]