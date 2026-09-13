from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from academics.models import AcademicYear, Term, SchoolClass
from .models import AdmissionApplication

from .services import AdmissionService
from accounts.decorators import role_required
from django.contrib.auth.decorators import login_required

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

@login_required
@role_required("admin")
def admission_list(request):

    applications = AdmissionApplication.objects.select_related(
        "academic_year",
        "term",
        "desired_class",
    ).order_by("-submitted_at")

    return render(
        request,
        "admissions/admission_list.html",
        {
            "applications": applications,
        },
    )

@login_required
@role_required("admin")
def admission_detail(request, application_id):

    application = get_object_or_404(
        AdmissionApplication,
        id=application_id,
    )

    return render(
        request,
        "admissions/admission_detail.html",
        {
            "application": application,
        },
    )

@login_required
@role_required("admin")
def approve_application(request, application_id):

    if request.method != "POST":
        return redirect(
            "admissions:admission_detail",
            application_id=application_id,
        )

    application = get_object_or_404(
        AdmissionApplication,
        id=application_id,
    )

    try:

        student, temporary_password = (
            AdmissionService.approve_application(
                application
            )
        )

        messages.success(
            request,
            "Admission application approved successfully.",
        )

    except ValueError as e:

        messages.error(
            request,
            str(e),
        )

    return redirect(
        "admissions:admission_detail",
        application_id=application_id,
    )

@login_required
@role_required("admin")
def reject_application(request, application_id):

    if request.method != "POST":
        return redirect(
            "admissions:admission_detail",
            application_id=application_id,
        )

    application = get_object_or_404(
        AdmissionApplication,
        id=application_id,
    )

    try:

        AdmissionService.reject_application(
            application
        )

        messages.success(
            request,
            "Admission application rejected.",
        )

    except ValueError as e:

        messages.error(
            request,
            str(e),
        )

    return redirect(
        "admissions:admission_detail",
        application_id=application_id,
    )