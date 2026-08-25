from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.crypto import get_random_string

from .models import (
    Teacher,
    TeachingAssignment,
    ClassTeacherAssignment,
)


User = get_user_model()


class TeacherService:

    # --------------------------------
    # TEACHER
    # --------------------------------

    @classmethod
    @transaction.atomic
    def create_teacher(
        cls,
        username,
        first_name,
        last_name,
        email,
        qualification,
        phone,
        date_joined,
    ):

        temporary_password = get_random_string(
            length=10
        )

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=temporary_password,
            role="teacher",
        )
        user.must_change_password = True

        user.save(
            update_fields=[
                "must_change_password",
            ]
        )

        teacher = Teacher.objects.create(
            user=user,
            qualification=qualification,
            phone=phone,
            date_joined=date_joined,
        )

        return teacher, temporary_password
    # --------------------------------
    # UPDATE TEACHER
    # --------------------------------

    @classmethod
    @transaction.atomic
    def update_teacher(
        cls,
        teacher,
        first_name,
        last_name,
        email,
        qualification,
        phone,
        date_joined,
    ):

        user = teacher.user

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        teacher.qualification = qualification
        teacher.phone = phone
        teacher.date_joined = date_joined
        teacher.save()

        return teacher

    # --------------------------------
    # SUBJECT TEACHER ASSIGNMENT
    # --------------------------------

    @classmethod
    @transaction.atomic
    def assign_subject_teacher(
        cls,
        teacher,
        class_subject,
        academic_year,
    ):

        assignment, created = (
            TeachingAssignment.objects.get_or_create(
                teacher=teacher,
                class_subject=class_subject,
                academic_year=academic_year,
                defaults={
                    "is_active": True,
                },
            )
        )

        return assignment, created

    # --------------------------------
    # CLASS TEACHER ASSIGNMENT
    # --------------------------------

    @classmethod
    @transaction.atomic
    def assign_class_teacher(
        cls,
        teacher,
        school_class,
        academic_year,
    ):

        assignment, created = (
            ClassTeacherAssignment.objects.update_or_create(
                school_class=school_class,
                academic_year=academic_year,
                defaults={
                    "teacher": teacher,
                    "is_active": True,
                },
            )
        )

        return assignment, created

    # --------------------------------
    # TEACHER ASSIGNMENTS
    # --------------------------------

    @staticmethod
    def get_teacher_assignments(
        teacher,
        academic_year=None,
    ):

        assignments = (
            teacher
            .teaching_assignments
            .select_related(
                "class_subject",
                "class_subject__school_class",
                "class_subject__subject",
                "academic_year",
            )
        )

        if academic_year:

            assignments = assignments.filter(
                academic_year=academic_year
            )

        return assignments.order_by(
            "class_subject__school_class__name",
            "class_subject__subject__name",
        )

    # --------------------------------
    # CLASS TEACHER ASSIGNMENTS
    # --------------------------------

    @staticmethod
    def get_class_teacher_assignments(
        teacher,
        academic_year=None,
    ):

        assignments = (
            teacher
            .class_teacher_assignments
            .select_related(
                "school_class",
                "academic_year",
            )
        )

        if academic_year:

            assignments = assignments.filter(
                academic_year=academic_year
            )

        return assignments.order_by(
            "school_class__name"
        )

# # from django.db import transaction

# # from .models import (
# #     TeachingAssignment,
# # )


# class TeachingAssignmentService:

#     @classmethod
#     @transaction.atomic
#     def assign_subject(
#         cls,
#         teacher,
#         class_subject,
#         academic_year,
#     ):

#         assignment, created = (
#             TeachingAssignment.objects.get_or_create(
#                 teacher=teacher,
#                 class_subject=class_subject,
#                 academic_year=academic_year,
#                 defaults={
#                     "is_active": True,
#                 },
#             )
#         )

#         if not created:

#             assignment.is_active = True

#             assignment.save(
#                 update_fields=[
#                     "is_active",
#                 ]
#             )

#         return assignment

#     @classmethod
#     @transaction.atomic
#     def deactivate_assignment(
#         cls,
#         assignment,
#     ):

#         assignment.is_active = False

#         assignment.save(
#             update_fields=[
#                 "is_active",
#             ]
#         )

#         return assignment