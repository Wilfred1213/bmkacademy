from datetime import date

from django.db import transaction
from django.utils import timezone

from academics.models import AcademicYear, Term
from students.models import Student, Enrollment

from .models import AdmissionApplication
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from accounts.models import ParentProfile


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
    @transaction.atomic
    def submit_application(
        cls,
        *,
        academic_year,
        term,
        desired_class,
        first_name,
        middle_name="",
        last_name,
        date_of_birth,
        gender,
        previous_school="",
        parent_name=None,
        parent_phone=None,
        parent_email="",
        parent_address="",
        relationship="guardian",
        applicant=None,
    ):

        # --------------------------------
        # VALIDATE ACADEMIC YEAR / TERM
        # --------------------------------

        if term.academic_year_id != academic_year.id:

            raise ValueError(
                "The selected term does not belong "
                "to the selected academic year."
            )

        # --------------------------------
        # CREATE APPLICATION
        # --------------------------------

        application = AdmissionApplication(
            applicant=applicant,

            academic_year=academic_year,

            term=term,

            desired_class=desired_class,

            first_name=first_name.strip(),

            middle_name=middle_name.strip(),

            last_name=last_name.strip(),

            date_of_birth=date_of_birth,

            gender=gender,

            previous_school=previous_school.strip(),

            parent_name=parent_name.strip()
            if parent_name
            else "",

            parent_phone=parent_phone.strip()
            if parent_phone
            else "",

            parent_email=parent_email.strip(),

            parent_address=parent_address.strip(),

            relationship=relationship,
        )

        # --------------------------------
        # MODEL VALIDATION
        # --------------------------------

        application.full_clean()

        # --------------------------------
        # SAVE
        # --------------------------------

        application.save()

        return application

    @classmethod
    @transaction.atomic
    def approve_application(cls, application):

        if application.status != "pending":
            raise ValueError(
                "Only pending applications can be approved."
            )

        # Create or retrieve the parent account
        parent_profile, temporary_password = (
            cls.create_parent_account(application)
        )

        # Create the student
        student = Student.objects.create(
            first_name=application.first_name,
            middle_name=application.middle_name,
            last_name=application.last_name,
            date_of_birth=application.date_of_birth,
            gender=application.gender,
            date_admitted=timezone.now().date(),
        )

        # Connect parent to student
        if parent_profile:
            student.parents.add(parent_profile)

        # Create enrollment
        Enrollment.objects.create(
            student=student,
            academic_year=application.academic_year,
            term=application.term,
            school_class=application.desired_class,
            is_current=True,
        )

        # Approve application
        application.status = "approved"
        application.reviewed_at = timezone.now()

        application.save(
            update_fields=[
                "status",
                "reviewed_at",
            ]
        )

        return student, temporary_password

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

        temporary_password = get_random_string(12)

        user = User.objects.create_user(
            username=username,
            email=application.parent_email,
            first_name=application.parent_name,
            role="parent",
            password=temporary_password,
        )

        user.must_change_password = True
        user.save(update_fields=["must_change_password"])

        parent_profile = ParentProfile.objects.create(
            user=user,
            phone=application.parent_phone,
            address=application.parent_address,
        )

        return parent_profile, temporary_password
