from datetime import date

from django.db import transaction
from django.utils import timezone

from academics.models import AcademicYear, Term
from students.models import Student, Enrollment

from .models import AdmissionApplication


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
    def approve_application(cls, application):

        if application.status != "pending":
            raise ValueError(
                "Only pending applications can be approved."
            )

        student = Student.objects.create(
            first_name=application.first_name,
            middle_name=application.middle_name,
            last_name=application.last_name,
            date_of_birth=application.date_of_birth,
            gender=application.gender,
            admission_number=cls.generate_admission_number(),
            date_admitted=timezone.now().date(),
        )

        # Connect applicant to student
        if application.applicant:

            parent_profile = getattr(
                application.applicant,
                "parent_profile",
                None
            )

            if parent_profile:
                student.parents.add(parent_profile)

        # Create enrollment
        Enrollment.objects.create(
            student=student,
            academic_year=cls.get_current_academic_year(),
            term=cls.get_current_term(),
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

        return student




# from datetime import date

# from django.db import transaction
# from django.utils import timezone

# from academics.models import AcademicYear, Term
# from students.models import Student, Enrollment


# def generate_admission_number():

#     year = date.today().year

#     last_student = (
#         Student.objects
#         .filter(
#             admission_number__startswith=f"BMK-{year}-"
#         )
#         .order_by("-id")
#         .first()
#     )

#     if last_student:

#         last_number = int(
#             last_student.admission_number.split("-")[-1]
#         )

#         next_number = last_number + 1

#     else:

#         next_number = 1

#     return f"BMK-{year}-{next_number:04d}"


# def get_current_academic_year():

#     academic_year = (
#         AcademicYear.objects
#         .filter(is_current=True)
#         .first()
#     )

#     if not academic_year:
#         raise ValueError(
#             "No current academic year has been configured."
#         )

#     return academic_year


# def get_current_term():

#     term = (
#         Term.objects
#         .filter(
#             is_current=True,
#             academic_year__is_current=True,
#         )
#         .first()
#     )

#     if not term:
#         raise ValueError(
#             "No current term has been configured."
#         )

#     return term


# @transaction.atomic
# def approve_application(application):

#     if application.status != "pending":

#         raise ValueError(
#             "Only pending applications can be approved."
#         )

#     student = Student.objects.create(

#         first_name=application.first_name,

#         middle_name=application.middle_name,

#         last_name=application.last_name,

#         date_of_birth=application.date_of_birth,

#         gender=application.gender,

#         admission_number=generate_admission_number(),

#         date_admitted=timezone.now().date(),
#     )

#     if application.applicant:

#         parent_profile = getattr(
#             application.applicant,
#             "parent_profile",
#             None
#         )

#         if parent_profile:

#             student.parents.add(parent_profile)

#     Enrollment.objects.create(

#         student=student,

#         academic_year=get_current_academic_year(),

#         term=get_current_term(),

#         school_class=application.desired_class,

#         is_current=True,
#     )

#     application.status = "approved"

#     application.reviewed_at = timezone.now()

#     application.save(
#         update_fields=[
#             "status",
#             "reviewed_at",
#         ]
#     )

#     return student