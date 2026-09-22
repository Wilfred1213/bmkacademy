from datetime import date

from django.db import transaction
from django.utils import timezone
from accounts.models import User
from academics.models import AcademicYear, Term
from students.models import Student, Enrollment
from django.urls import reverse
from .models import AdmissionApplication
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from accounts.models import ParentProfile
from notifications.services import NotificationService
from notifications.email_service import NotificationEmailService
from datetime import timedelta
import uuid


class AdmissionService:

    @staticmethod
    def generate_admission_number():

        year = date.today().year

        last_student = (
            Student.objects
            .filter(
                admission_number__startswith=f"BMK-{year}-"
            )
            .order_by("-id")
            .first()
        )

        if last_student:
            last_number = int(
                last_student.admission_number.split("-")[-1]
            )

            next_number = last_number + 1

        else:
            next_number = 1

        return f"BMK-{year}-{next_number:04d}"

    @staticmethod
    def get_current_academic_year():

        academic_year = (
            AcademicYear.objects
            .filter(is_current=True)
            .first()
        )

        if not academic_year:
            raise ValueError(
                "No current academic year has been configured."
            )

        return academic_year

    @staticmethod
    def get_current_term():

        term = (
            Term.objects
            .filter(
                is_current=True,
                academic_year__is_current=True,
            )
            .first()
        )

        if not term:
            raise ValueError(
                "No current term has been configured."
            )

        return term

    @classmethod
    def submit_application(cls, applicant=None, **data):

        # -------------------------------------------------
        # 1. Check if this parent already has this child
        #    enrolled for the selected academic year/term
        # -------------------------------------------------

        if applicant:

            child_exists = applicant.parent_profile.children.filter(
                first_name=data["first_name"],
                middle_name=data.get("middle_name", ""),
                last_name=data["last_name"],
                date_of_birth=data["date_of_birth"],
            ).exists()

            if child_exists:

                already_enrolled = Enrollment.objects.filter(
                    student__parents__user=applicant,
                    student__first_name=data["first_name"],
                    student__middle_name=data.get("middle_name", ""),
                    student__last_name=data["last_name"],
                    student__date_of_birth=data["date_of_birth"],
                    academic_year=data["academic_year"],
                    term=data["term"],
                ).exists()

                if already_enrolled:
                    raise ValueError(
                        "This student is already enrolled for "
                        "the selected academic year and term."
                    )


        # -------------------------------------------------
        # 2. Check for an existing admission application
        # -------------------------------------------------

        duplicate_exists = AdmissionApplication.objects.filter(
            first_name=data["first_name"],
            middle_name=data.get("middle_name", ""),
            last_name=data["last_name"],
            date_of_birth=data["date_of_birth"],
            academic_year=data["academic_year"],
            term=data["term"],
            status__in=["pending", "approved"],
        ).exists()

        if duplicate_exists:
            raise ValueError(
                "An admission application already exists for this "
                "student for the selected academic year and term."
            )


        # -------------------------------------------------
        # 3. Create the application
        # -------------------------------------------------

        application = AdmissionApplication(
            applicant=applicant,
            **data,
        )

        application.full_clean()
        application.save()


        # -------------------------------------------------
        # 4. Notify administrators
        # -------------------------------------------------

        admin_users = User.objects.filter(
            role="admin",
            is_active=True,
        )

        for admin_user in admin_users:

            NotificationService.create_notification(
                recipient=admin_user,
                title="New Admission Application",
                message=(
                    f"A new admission application has been submitted "
                    f"for {application.first_name} "
                    f"{application.last_name} "
                    f"for {application.desired_class}."
                ),
                notification_type="admission",
                link=reverse(
                    "admissions:admission_detail",
                    kwargs={
                        "application_id": application.id
                    },
                ),
            )

        return application
    @classmethod
    @transaction.atomic
    def approve_application(cls, application):
        if application.status != "pending":
            raise ValueError(
                "Only pending applications can be approved."
            )

        # ---------------------------------------------------------
        # 1. Generate secure claim token
        # ---------------------------------------------------------

        application.claim_token = uuid.uuid4()

        application.claim_token_expires_at = (
            timezone.now() + timedelta(days=2)
        )

        # ---------------------------------------------------------
        # 2. Create the student
        # ---------------------------------------------------------

        student = Student.objects.create(
            first_name=application.first_name,
            middle_name=application.middle_name,
            last_name=application.last_name,
            date_of_birth=application.date_of_birth,
            gender=application.gender,
            date_admitted=timezone.now().date(),
        )
        
        # ---------------------------------------------------------
        # 3. Create enrollment
        # ---------------------------------------------------------

        enrollment = Enrollment.objects.create(
            student=student,
            academic_year=application.academic_year,
            term=application.term,
            school_class=application.desired_class,
            is_current=True,
        )

        # ---------------------------------------------------------
        # 4. Mark application as approved
        # ---------------------------------------------------------
        application.student = student
        application.status = "approved"
        application.reviewed_at = timezone.now()

        application.save(
            update_fields=[
                "status",
                "reviewed_at",
                "claim_token",
                "claim_token_expires_at",
                "student",
            ]
        )

        # ---------------------------------------------------------
        # 5. Send email only after transaction succeeds
        # ---------------------------------------------------------

        transaction.on_commit(
            lambda: NotificationEmailService
            .send_admission_decision_email(
                application,
                "approved",
            )
        )

        # ---------------------------------------------------------
        # 6. Notify an already-linked parent, if one exists
        # ---------------------------------------------------------

        if application.applicant:
            parent_profile = getattr(
                application.applicant,
                "parent_profile",
                None,
            )

            if parent_profile:

                NotificationService.create_notification(
                    recipient=parent_profile.user,
                    title="Admission Approved",
                    message=(
                        f"Congratulations! The admission "
                        f"application for "
                        f"{student.first_name} "
                        f"{student.last_name} "
                        f"has been approved. "
                        f"The student has been admitted into "
                        f"{enrollment.school_class}."
                    ),
                    notification_type="admission",
                    link=reverse(
                        "admissions:parent_admission_detail",
                        kwargs={
                            "application_id": application.id
                        },
                    ),
                )

        return student

    @classmethod
    def create_parent_account(cls, application):

        User = get_user_model()

        if application.applicant:

            parent_profile = getattr(
                application.applicant,
                "parent_profile",
                None,
            )

            if parent_profile:
                return parent_profile, None

        username = f"parent_{get_random_string(8)}"

        user = User.objects.create_user(
            username=username,
            email=application.parent_email,
            first_name=application.parent_name,
            role="parent",
            password=None,
            is_active=False,
        )

        parent_profile = ParentProfile.objects.create(
            user=user,
            phone=application.parent_phone,
            address=application.parent_address,
        )

        return parent_profile, None

    @classmethod
    @transaction.atomic
    def reject_application(cls, application):

        if application.status != "pending":
            raise ValueError(
                "Only pending applications can be rejected."
            )

        application.status = "rejected"
        application.reviewed_at = timezone.now()

        application.save(
            update_fields=[
                "status",
                "reviewed_at",
            ]
        )
        transaction.on_commit(
            lambda: NotificationEmailService.send_admission_decision_email(
                application,
                "rejected",
            )
        )

        # --------------------------------
        # NOTIFY PARENT
        # --------------------------------

        if application.applicant:

            parent_profile = getattr(
                application.applicant,
                "parent_profile",
                None,
            )

            if parent_profile:

                NotificationService.create_notification(
                    recipient=parent_profile.user,
                    title="Admission Application Rejected",
                    message=(
                        f"The admission application for "
                        f"{application.first_name} "
                        f"{application.last_name} "
                        f"has been rejected."
                    ),
                    notification_type="admission",
                    link=reverse(
                        "admissions:parent_admission_detail",
                        kwargs={
                            "application_id": application.id,
                        },
                    ),
                )

        return application

    @classmethod
    @transaction.atomic
    def claim_application(cls, application, username, password):
        User = get_user_model()

        # 1. Application must be approved
        if application.status != "approved":
            raise ValueError(
                "Only approved admission applications can be claimed."
            )

        # 2. Application must not have been claimed already
        if application.claimed_at:
            raise ValueError(
                "This admission application has already been claimed."
            )

        # 3. Claim token must exist
        if not application.claim_token:
            raise ValueError(
                "This admission claim link is no longer valid."
            )

        # 4. Check token expiration
        if (
            application.claim_token_expires_at
            and application.claim_token_expires_at < timezone.now()
        ):
            raise ValueError(
                "This admission claim link has expired."
            )

        # 5. Make sure username is not already taken
        if User.objects.filter(username=username).exists():
            raise ValueError(
                "This username is already taken."
            )

        # 6. Create the parent user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=application.parent_email,
            first_name=application.parent_name,
            role="parent",
            is_active=True,
        )

        # 7. Create ParentProfile
        parent_profile = ParentProfile.objects.create(
            user=user,
            phone=application.parent_phone,
            address=application.parent_address,
        )

        # 8. Connect the admission application to the parent
        application.student.parents.add(parent_profile)
        application.applicant = user
        application.claimed_at = timezone.now()

        # 9. Invalidate the claim link
        application.claim_token = None
        application.claim_token_expires_at = None

        application.save(
            update_fields=[
                "applicant",
                "claimed_at",
                "claim_token",
                "claim_token_expires_at",
            ]
        )

        # 10. Create an in-app notification
        NotificationService.create_notification(
            recipient=user,
            title="Welcome to BMK Academy",
            message=(
                f"Your parent account has been successfully created. "
                f"You can now access information about "
                f"{application.first_name} "
                f"{application.last_name}."
            ),
            notification_type="admission",
            link=reverse(
                "admissions:parent_admission_detail",
                kwargs={
                    "application_id": application.id
                },
            ),
        )

        return user, parent_profile

    @classmethod
    def resend_admission_email(cls, application):
        if application.status not in ["approved", "rejected"]:
            raise ValueError(
                "Only approved or rejected applications can have "
                "their decision email resent."
            )

        if not application.parent_email:
            raise ValueError(
                "This application does not have a parent email address."
            )

        if application.status == "approved":

            if application.claimed_at:
                raise ValueError(
                    "This application has already been claimed. "
                    "The claim email should not be resent."
                )

            if not application.claim_token:
                raise ValueError(
                    "This approved application has no active claim token."
                )

            decision = "approved"

        else:
            decision = "rejected"

        return NotificationEmailService.send_admission_decision_email(
            application,
            decision,
        )
    @classmethod
    @transaction.atomic
    def regenerate_claim_token(cls, application):

        if application.status != "approved":
            raise ValueError(
                "Only approved applications can have a new claim link."
            )

        if application.claimed_at:
            raise ValueError(
                "This application has already been claimed."
            )

        application.claim_token = uuid.uuid4()

        application.claim_token_expires_at = (
            timezone.now() + timedelta(days=2)
        )

        application.save(
            update_fields=[
                "claim_token",
                "claim_token_expires_at",
            ]
        )

        transaction.on_commit(
            lambda: NotificationEmailService
            .send_admission_decision_email(
                application,
                "approved",
            )
        )

        return application