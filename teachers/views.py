from datetime import datetime

from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from academics.models import (
    AcademicYear,
    ClassSubject,
    SchoolClass,
)

from .models import (
    Teacher,
    TeachingAssignment,
    ClassTeacherAssignment,
)

from .services import TeacherService



# --------------------------------
# TEACHER LIST
# --------------------------------

def teacher_list(request):

    teachers = (
        Teacher.objects
        .select_related("user")
        .order_by(
            "user__first_name",
            "user__last_name",
        )
    )

    return render(
        request,
        "teachers/teacher_list.html",
        {
            "teachers": teachers,
        },
    )


# --------------------------------
# ADD TEACHER
# --------------------------------

def create_teacher(request):

    if request.method == "POST":

        teacher, temporary_password = (
            TeacherService.create_teacher(
                username=request.POST["username"],
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
                email=request.POST["email"],
                qualification=request.POST.get(
                    "qualification",
                    "",
                ),
                phone=request.POST.get(
                    "phone",
                    "",
                ),
                date_joined=datetime.strptime(
                    request.POST["date_joined"],
                    "%Y-%m-%d",
                ).date(),
            )
        )

        messages.success(
            request,
            f"{teacher} was created successfully."
        )

        return render(
            request,
            "teachers/teacher_credentials.html",
            {
                "teacher": teacher,
                "temporary_password": temporary_password,
            },
        )

    return render(
        request,
        "teachers/teacher_form.html"
    )


# --------------------------------
# TEACHER DETAIL
# --------------------------------

def teacher_detail(
    request,
    teacher_id,
):

    teacher = get_object_or_404(
        Teacher.objects.select_related("user"),
        id=teacher_id,
    )

    academic_year_id = request.GET.get(
        "academic_year"
    )

    academic_year = None

    if academic_year_id:

        academic_year = get_object_or_404(
            AcademicYear,
            id=academic_year_id,
        )

    teaching_assignments = (
        TeacherService.get_teacher_assignments(
            teacher=teacher,
            academic_year=academic_year,
        )
    )

    class_teacher_assignments = (
        TeacherService.get_class_teacher_assignments(
            teacher=teacher,
            academic_year=academic_year,
        )
    )

    academic_years = AcademicYear.objects.order_by(
        "-start_date"
    )

    return render(
        request,
        "teachers/teacher_detail.html",
        {
            "teacher": teacher,
            "teaching_assignments": teaching_assignments,
            "class_teacher_assignments": (
                class_teacher_assignments
            ),
            "academic_years": academic_years,
            "selected_academic_year": (
                academic_year
            ),
        },
    )


# --------------------------------
# EDIT TEACHER
# --------------------------------

def update_teacher(
    request,
    teacher_id,
):

    teacher = get_object_or_404(
        Teacher,
        id=teacher_id,
    )

    if request.method == "POST":

        TeacherService.update_teacher(
            teacher=teacher,
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            email=request.POST["email"],
            qualification=request.POST.get(
                "qualification",
                "",
            ),
            phone=request.POST.get(
                "phone",
                "",
            ),
            date_joined=datetime.strptime(
                request.POST["date_joined"],
                "%Y-%m-%d",
            ).date(),
        )

        messages.success(
            request,
            f"{teacher} was updated successfully."
        )

        return redirect(
            "teachers:teacher_detail",
            teacher_id=teacher.id,
        )

    return render(
        request,
        "teachers/teacher_form.html",
        {
            "teacher": teacher,
        },
    )


# --------------------------------
# TEACHING ASSIGNMENT LIST
# --------------------------------

def teaching_assignment_list(request):

    assignments = (
        TeachingAssignment.objects
        .select_related(
            "teacher__user",
            "class_subject__school_class",
            "class_subject__subject",
            "academic_year",
        )
        .order_by(
            "-academic_year__start_date",
            "class_subject__school_class__name",
            "class_subject__subject__name",
        )
    )

    return render(
        request,
        "teachers/teaching_assignment_list.html",
        {
            "assignments": assignments,
        },
    )


# --------------------------------
# ASSIGN SUBJECT TEACHER
# --------------------------------

def assign_subject_teacher(request):

    teachers = (
        Teacher.objects
        .select_related("user")
        .filter(is_active=True)
        .order_by(
            "user__first_name",
        )
    )

    academic_years = AcademicYear.objects.order_by(
        "-start_date"
    )

    class_subjects = (
        ClassSubject.objects
        .select_related(
            "school_class",
            "subject",
        )
        .filter(
            is_active=True,
        )
        .order_by(
            "school_class__name",
            "subject__name",
        )
    )

    if request.method == "POST":

        teacher = get_object_or_404(
            Teacher,
            id=request.POST["teacher"],
            is_active=True,
        )

        academic_year = get_object_or_404(
            AcademicYear,
            id=request.POST["academic_year"],
        )

        class_subject = get_object_or_404(
            ClassSubject,
            id=request.POST["class_subject"],
            is_active=True,
        )

        assignment, created = (
            TeacherService.assign_subject_teacher(
                teacher=teacher,
                class_subject=class_subject,
                academic_year=academic_year,
            )
        )

        if created:

            messages.success(
                request,
                "Teacher assigned successfully."
            )

        else:

            messages.info(
                request,
                "This teaching assignment already exists."
            )

        return redirect(
            "teachers:teaching_assignment_list"
        )

    return render(
        request,
        "teachers/teaching_assignment_form.html",
        {
            "teachers": teachers,
            "academic_years": academic_years,
            "class_subjects": class_subjects,
        },
    )


# --------------------------------
# CLASS TEACHER LIST
# --------------------------------

def class_teacher_assignment_list(request):

    assignments = (
        ClassTeacherAssignment.objects
        .select_related(
            "teacher__user",
            "school_class",
            "academic_year",
        )
        .order_by(
            "-academic_year__start_date",
            "school_class__name",
        )
    )

    return render(
        request,
        "teachers/class_teacher_assignment_list.html",
        {
            "assignments": assignments,
        },
    )


# --------------------------------
# ASSIGN CLASS TEACHER
# --------------------------------

def assign_class_teacher(request):

    teachers = (
        Teacher.objects
        .select_related("user")
        .filter(
            is_active=True
        )
        .order_by(
            "user__first_name",
        )
    )

    school_classes = SchoolClass.objects.order_by(
        "section",
        "name",
    )

    academic_years = AcademicYear.objects.order_by(
        "-start_date"
    )

    if request.method == "POST":

        teacher = get_object_or_404(
            Teacher,
            id=request.POST["teacher"],
            is_active=True,
        )

        school_class = get_object_or_404(
            SchoolClass,
            id=request.POST["school_class"],
        )

        academic_year = get_object_or_404(
            AcademicYear,
            id=request.POST["academic_year"],
        )

        assignment, created = (
            TeacherService.assign_class_teacher(
                teacher=teacher,
                school_class=school_class,
                academic_year=academic_year,
            )
        )

        if created:

            messages.success(
                request,
                "Class teacher assigned successfully."
            )

        else:

            messages.success(
                request,
                "Class teacher assignment updated successfully."
            )

        return redirect(
            "teachers:class_teacher_assignment_list"
        )

    return render(
        request,
        "teachers/class_teacher_assignment_form.html",
        {
            "teachers": teachers,
            "school_classes": school_classes,
            "academic_years": academic_years,
        },
    )