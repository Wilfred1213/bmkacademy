from django.shortcuts import render, get_object_or_404

from .models import Student
from datetime import datetime

from academics.models import SchoolClass

from attendance.models import Attendance
from attendance.services import AttendanceService


def student_list(request):

    students = Student.objects.all().order_by(
        "first_name",
        "last_name",
    )

    return render(
        request,
        "students/student_list.html",
        {
            "students": students,
        },
    )



def student_detail(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id,
    )

    current_enrollment = (
        student.enrollments
        .filter(is_current=True)
        .select_related(
            "school_class",
            "academic_year",
            "term",
        )
        .first()
    )

    
    enrollment_history = (
        student.enrollments
        .select_related(
            "school_class",
            "academic_year",
            "term",
        )
        .order_by(
            "-academic_year__start_date",
            "-term__start_date",
        )
    )

    statistics = AttendanceService.get_student_statistics(
        student=student,
    )

    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "current_enrollment": current_enrollment,
            "enrollment_history": enrollment_history,
            "statistics": statistics,
        },
    )