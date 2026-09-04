from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from academics.models import AcademicYear, Term, SchoolClass

from .services import AdmissionService


from .forms import AdmissionApplicationForm



def _admission_error(request, message):

    if request.headers.get("HX-Request"):

        return render(
            request,
            "admissions/partials/application_error.html",
            {
                "message": message,
            },
            status=400,
        )

    return HttpResponse(
        message,
        status=400,
    )


def admission_application(request):

    if request.method == "POST":

        form = AdmissionApplicationForm(request.POST)

        if form.is_valid():

            application = AdmissionService.submit_application(
                **form.cleaned_data,
                applicant=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
            )

            if request.headers.get("HX-Request"):

                return render(
                    request,
                    "admissions/partials/application_success.html",
                    {
                        "application": application,
                    },
                )

            return render(
                request,
                "admissions/application_success.html",
                {
                    "application": application,
                },
            )

        # -----------------------------------------
        # INVALID FORM
        # -----------------------------------------

        if request.headers.get("HX-Request"):

            return render(
                request,
                "admissions/partials/admission_form.html",
                {
                    "form": form,
                },
                status=400,
            )

    else:

        form = AdmissionApplicationForm()

    # ---------------------------------------------
    # NORMAL PAGE
    # ---------------------------------------------

    return render(
        request,
        "admissions/admission_application.html",
        {
            "form": form,
        },
    )


def admission_terms(request):

    academic_year_id = request.GET.get(
        "academic_year"
    )

    if not academic_year_id:

        return HttpResponse(
            '<option value="">Select Term</option>'
        )

    terms = (
        Term.objects
        .filter(
            academic_year_id=academic_year_id
        )
        .order_by("start_date")
    )

    return render(
        request,
        "admissions/partials/term_options.html",
        {
            "terms": terms,
        },
    )