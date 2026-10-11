from django.shortcuts import render, get_object_or_404

from .models import Student
from datetime import datetime

from academics.models import SchoolClass

from attendance.models import Attendance
from attendance.services import AttendanceService
from teachers.models import TeachingAssignment, ClassTeacherAssignment
  
from django.db.models import Q

# from django.db.models import Q

# from django.db.models import Q
# from teachers.models import Teacher, TeachingAssignment, ClassTeacherAssignment

def student_list(request):
    q = request.GET.get('q', '').strip()
    user = request.user
    students = Student.objects.all()

    # TEACHER: only students in his assigned classes
    if hasattr(user, 'role') and user.role == 'teacher':
        try:
            teacher_profile = user.teacher_profile  # Teacher has OneToOne to User
        except Teacher.DoesNotExist:
            teacher_profile = None

        if teacher_profile:
            taught_class_ids = TeachingAssignment.objects.filter(
                teacher=teacher_profile,
                is_active=True
            ).values_list('class_subject__school_class_id', flat=True)

            class_teacher_class_ids = ClassTeacherAssignment.objects.filter(
                teacher=teacher_profile,
                is_active=True
            ).values_list('school_class_id', flat=True)

            allowed_ids = list(set(list(taught_class_ids) + list(class_teacher_class_ids)))

            if allowed_ids:
                # Enrollment has is_current = True in your attendance view
                students = students.filter(
                    enrollments__school_class_id__in=allowed_ids,
                    enrollments__is_current=True
                ).distinct()
            else:
                students = Student.objects.none()
        else:
            students = Student.objects.none()

    if q:
        students = students.filter(
            Q(first_name__icontains=q) |
            Q(middle_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(admission_number__icontains=q)
        )

    students = students.order_by('first_name')

    return render(request, 'students/student_list.html', {
        'students': students,
        'q': q
    })
    # def student_list(request):

#     students = Student.objects.all().order_by(
#         "first_name",
#         "last_name",
#     )

#     return render(
#         request,
#         "students/student_list.html",
#         {
#             "students": students,
#         },
#     )



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