from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from academics.models import AcademicYear, Term, SchoolClass
from .models import AdmissionApplication
from django.utils import timezone
from .services import AdmissionService
from accounts.decorators import role_required
from django.contrib.auth.decorators import login_required

from .forms import AdmissionApplicationForm, ClaimApplicationForm

from django.contrib.auth import login


 

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

            try:

                application = AdmissionService.submit_application(
                    **form.cleaned_data,
                    applicant=(
                        request.user
                        if request.user.is_authenticated
                        else None
                    ),
                )

            except ValueError as exc:

                form.add_error(
                    None,
                    str(exc),
                )

            else:

                if request.headers.get("HX-Request"):

                    return render(
                        request,
                        "admissions/partials/application_success.html",
                        {
                            "application": application
                        },
                    )

                return render(
                    request,
                    "admissions/application_success.html",
                    {
                        "application": application
                    },
                )

        if request.headers.get("HX-Request"):

            return render(
                request,
                "admissions/partials/admission_form.html",
                {
                    "form": form
                },
                # status=400,
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

    application = get_object_or_404(
        AdmissionApplication,
        id=application_id,
    )

    if request.method == "POST":

        try:

            student = AdmissionService.approve_application(
                application
            )

            messages.success(
                request,
                (
                    f"Admission for "
                    f"{student.first_name} "
                    f"{student.last_name} "
                    f"was approved successfully."
                ),
            )

        except ValueError as exc:

            messages.error(
                request,
                str(exc),
            )

    return redirect(
        "admissions:admission_detail",
        application_id=application.id,
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

@login_required
@role_required("parent")
def parent_admission_detail(request, application_id):

    application = get_object_or_404(
        AdmissionApplication.objects.select_related(
            "academic_year",
            "term",
            "desired_class",
            "student",
        ),
        id=application_id,
        applicant=request.user,
    )

    return render(
        request,
        "admissions/parent_admission_detail.html",
        {
            "application": application,
        },
    )



def claim_application(request, claim_token):

    application = get_object_or_404(
        AdmissionApplication,
        claim_token=claim_token,
    )

    # Already claimed
    if application.claimed_at:

        messages.info(
            request,
            "This admission application has already been claimed.",
        )

        return redirect("accounts:login")

    # Expired
    if (
        application.claim_token_expires_at
        and application.claim_token_expires_at < timezone.now()
    ):
        return render(
            request,
            "admissions/claim_expired.html",
            {
                "application": application,
            },
        )

    if request.method == "POST":

        form = ClaimApplicationForm(request.POST)

        if form.is_valid():

            try:

                user, parent_profile = (
                    AdmissionService.claim_application(
                        application=application,
                        username=form.cleaned_data["username"],
                        password=form.cleaned_data["password"],
                    )
                )

            except ValueError as exc:

                form.add_error(
                    None,
                    str(exc),
                )

            else:

                login(request, user)

                return redirect(
                    "accounts:parent_home"
                )

    else:

        form = ClaimApplicationForm()

    return render(
        request,
        "admissions/claim_application.html",
        {
            "application": application,
            "form": form,
        },
    )



@login_required
@role_required("admin")
def resend_admission_email(request, application_id):

    application = get_object_or_404(
        AdmissionApplication,
        id=application_id,
    )

    if request.method != "POST":
        return redirect(
            "admissions:admission_detail",
            application_id=application.id,
        )

    try:

        sent = AdmissionService.resend_admission_email(
            application
        )

    except ValueError as exc:

        messages.error(
            request,
            str(exc),
        )

    else:

        if sent:

            messages.success(
                request,
                "Admission decision email was sent successfully.",
            )

        else:

            messages.error(
                request,
                (
                    "The admission email could not be sent. "
                    "Please check the email status for details."
                ),
            )

    return redirect(
        "admissions:admission_detail",
        application_id=application.id,
    )

@login_required
@role_required("admin")
def regenerate_claim_token(request, application_id):

    application = get_object_or_404(
        AdmissionApplication,
        id=application_id,
    )

    if request.method != "POST":
        return redirect(
            "admissions:admission_detail",
            application_id=application.id,
        )

    try:
        AdmissionService.regenerate_claim_token(
            application
        )

        messages.success(
            request,
            "A new admission claim link has been generated. "
            "The admission email will be sent using the new link.",
        )

    except ValueError as exc:

        messages.error(
            request,
            str(exc),
        )

    return redirect(
        "admissions:admission_detail",
        application_id=application.id,
    )