from datetime import datetime

from django.shortcuts import (
    get_object_or_404,
    render,
)

from academics.models import SchoolClass
from teachers.models import Teacher, ClassTeacherAssignment
from students.models import Student

from .models import Attendance
from .services import AttendanceService




from datetime import datetime

from django.shortcuts import (
    get_object_or_404,
    render,
)

from accounts.decorators import role_required
from django.contrib.auth.decorators import login_required
from datetime import datetime, date



@login_required
@role_required("admin", "teacher")
def mark_attendance(request):

    # --------------------------------------------------
    # Determine which classes the user is allowed to see
    # --------------------------------------------------

    if request.user.role == "admin":

        classes = SchoolClass.objects.all()

    else:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
            is_active=True,
        )

        classes = SchoolClass.objects.filter(
            class_teacher_assignments__teacher=teacher,
            class_teacher_assignments__is_active=True,
        ).distinct()


    selected_class = None
    students = []
    attendance_date = None
    statistics = None
    attendance_saved = False

    existing_attendance = {}


    # ==================================================
    # GET
    # ==================================================

    if request.method == "GET":

        selected_class_id = request.GET.get(
            "school_class"
        )

        requested_date = request.GET.get(
            "attendance_date"
        )


        # --------------------------------------------------
        # Automatically select class for a teacher
        # --------------------------------------------------

        if (
            request.user.role == "teacher"
            and not selected_class_id
            and classes.count() == 1
        ):

            selected_class = classes.first()

        elif selected_class_id:

            selected_class = get_object_or_404(
                classes,
                id=selected_class_id,
            )


        # --------------------------------------------------
        # Default to today's date
        # --------------------------------------------------

        if requested_date:

            attendance_date = datetime.strptime(
                requested_date,
                "%Y-%m-%d",
            ).date()

        else:

            attendance_date = date.today()


        # --------------------------------------------------
        # Load students
        # --------------------------------------------------

        if selected_class:

            students = Student.objects.filter(
                enrollments__school_class=selected_class,
                enrollments__is_current=True,
            ).distinct()


            # --------------------------------------------------
            # Existing attendance
            # --------------------------------------------------

            records = Attendance.objects.filter(
                student__in=students,
                attendance_date=attendance_date,
            )

            existing_attendance = {
                record.student_id: record.status
                for record in records
            }


            if records.exists():

                statistics = (
                    AttendanceService
                    .get_class_statistics(
                        selected_class,
                        attendance_date,
                    )
                )


    # ==================================================
    # POST
    # ==================================================

    elif request.method == "POST":

        selected_class = get_object_or_404(
            classes,
            id=request.POST["school_class"],
        )

        attendance_date = datetime.strptime(
            request.POST["attendance_date"],
            "%Y-%m-%d",
        ).date()


        students = Student.objects.filter(
            enrollments__school_class=selected_class,
            enrollments__is_current=True,
        ).distinct()


        attendance_data = {}


        for student in students:

            status = request.POST.get(
                f"student_{student.id}"
            )

            if status:

                attendance_data[student.id] = status


        # --------------------------------------------------
        # Save attendance
        # --------------------------------------------------

        AttendanceService.mark_class_attendance(
            school_class=selected_class,
            attendance_date=attendance_date,
            attendance_data=attendance_data,
        )


        # --------------------------------------------------
        # Get updated statistics
        # --------------------------------------------------

        statistics = (
            AttendanceService
            .get_class_statistics(
                selected_class,
                attendance_date,
            )
        )


        # --------------------------------------------------
        # Reload saved records
        # --------------------------------------------------

        records = Attendance.objects.filter(
            student__in=students,
            attendance_date=attendance_date,
        )


        existing_attendance = {
            record.student_id: record.status
            for record in records
        }


        attendance_saved = True


    # ==================================================
    # Attach status to each student
    # ==================================================

    for student in students:

        student.attendance_status = (
            existing_attendance.get(
                student.id
            )
        )


    # ==================================================
    # Response
    # ==================================================

    return render(
        request,
        "attendance/mark_attendance.html",
        {
            "classes": classes,
            "selected_class": selected_class,
            "students": students,
            "attendance_date": attendance_date,
            "statistics": statistics,
            "attendance_saved": attendance_saved,
            "existing_attendance": existing_attendance,
        },
    )

@login_required
@role_required("admin", "teacher")
def attendance_history(request):

    if request.user.role == "admin":

        classes = SchoolClass.objects.all()

    else:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
            is_active=True,
        )

        classes = SchoolClass.objects.filter(
            class_teacher_assignments__teacher=teacher,
            class_teacher_assignments__is_active=True,
        ).distinct()


    selected_class = None
    records = []

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")


    if request.GET.get("school_class"):

        selected_class = get_object_or_404(
            classes,
            id=request.GET["school_class"],
        )

        parsed_start_date = None
        parsed_end_date = None


        if start_date:

            parsed_start_date = datetime.strptime(
                start_date,
                "%Y-%m-%d",
            ).date()


        if end_date:

            parsed_end_date = datetime.strptime(
                end_date,
                "%Y-%m-%d",
            ).date()


        records = AttendanceService.get_class_attendance_history(
            school_class=selected_class,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
        )


    return render(
        request,
        "attendance/attendance_history.html",
        {
            "classes": classes,
            "selected_class": selected_class,
            "records": records,
            "start_date": start_date,
            "end_date": end_date,
        },
    )

def student_attendance(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id,
    )

    start_date = request.GET.get(
        "start_date"
    )

    end_date = request.GET.get(
        "end_date"
    )

    parsed_start_date = None
    parsed_end_date = None

    if start_date:

        parsed_start_date = datetime.strptime(
            start_date,
            "%Y-%m-%d",
        ).date()

    if end_date:

        parsed_end_date = datetime.strptime(
            end_date,
            "%Y-%m-%d",
        ).date()

    records = AttendanceService.get_student_attendance(
        student=student,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
    )

    statistics = AttendanceService.get_student_statistics(
        student=student,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
    )

    return render(
        request,
        "attendance/student_attendance.html",
        {
            "student": student,
            "records": records,
            "statistics": statistics,
            "start_date": start_date,
            "end_date": end_date,
        },
    )

# @login_required
# @role_required("admin", "teacher")
# def attendance_dashboard(request):

#     if request.user.role == "admin":
#         classes = SchoolClass.objects.all()
#     else:
#         teacher = get_object_or_404(
#             Teacher,
#             user=request.user,
#             is_active=True,
#         )

#         classes = SchoolClass.objects.filter(
#             class_teacher_assignments__teacher=teacher,
#             class_teacher_assignments__is_active=True,
#         ).distinct()

#     selected_class = None
#     statistics = None

#     if request.GET.get("school_class"):

#         selected_class = get_object_or_404(
#             classes,
#             id=request.GET["school_class"],
#         )

#         statistics = AttendanceService.get_class_statistics(
#             selected_class
#         )

#     return render(
#         request,
#         "attendance/attendance_dashboard.html",
#         {
#             "classes": classes,
#             "selected_class": selected_class,
#             "statistics": statistics,
#         },
#     )

@login_required
@role_required("admin", "teacher")
def attendance_dashboard(request):

    if request.user.role == "admin":

        classes = SchoolClass.objects.all()

    else:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
            is_active=True,
        )

        classes = SchoolClass.objects.filter(
            class_teacher_assignments__teacher=teacher,
            class_teacher_assignments__is_active=True,
        ).distinct()

    selected_class = None
    statistics = None

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if request.GET.get("school_class"):

        selected_class = get_object_or_404(
            classes,
            id=request.GET["school_class"],
        )

        parsed_start_date = None
        parsed_end_date = None

        if start_date:
            parsed_start_date = datetime.strptime(
                start_date,
                "%Y-%m-%d",
            ).date()

        if end_date:
            parsed_end_date = datetime.strptime(
                end_date,
                "%Y-%m-%d",
            ).date()

        statistics = AttendanceService.get_class_period_statistics(
            school_class=selected_class,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
        )

    return render(
        request,
        "attendance/attendance_dashboard.html",
        {
            "classes": classes,
            "selected_class": selected_class,
            "statistics": statistics,
            "start_date": start_date,
            "end_date": end_date,
        },
    )