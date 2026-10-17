from rest_framework import viewsets, filters
from.models import Student
from.serializers import StudentSerializer
from teachers.models import Teacher, TeachingAssignment, ClassTeacherAssignment

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'middle_name', 'last_name', 'admission_number']

    def get_queryset(self):
        user = self.request.user
        qs = Student.objects.all().order_by('first_name')

        # Same logic we fixed for teacher
        if hasattr(user, 'role') and user.role == 'teacher':
            try:
                teacher = user.teacher_profile
                taught = TeachingAssignment.objects.filter(teacher=teacher, is_active=True).values_list('class_subject__school_class_id', flat=True)
                ct = ClassTeacherAssignment.objects.filter(teacher=teacher, is_active=True).values_list('school_class_id', flat=True)
                allowed = list(set(list(taught)+list(ct)))
                if allowed:
                    qs = qs.filter(enrollments__school_class_id__in=allowed, enrollments__is_current=True).distinct()
                else:
                    qs = Student.objects.none()
            except:
                qs = Student.objects.none()
        return qs