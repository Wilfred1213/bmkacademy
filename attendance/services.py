from django.db import transaction
from django.db.models import Count, Q

from students.models import Student

from .models import Attendance


class AttendanceService:

    @classmethod
    @transaction.atomic
    def mark_attendance(
        cls,
        student,
        attendance_date,
        status,
        remarks="",
    ):
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            attendance_date=attendance_date,
            defaults={
                "status": status,
                "remarks": remarks,
            },
        )

        if not created:
            attendance.status = status
            attendance.remarks = remarks
            attendance.save()

        return attendance

    @classmethod
    @transaction.atomic
    def mark_class_attendance(
        cls,
        school_class,
        attendance_date,
        attendance_data,
    ):
        students = Student.objects.filter(
            enrollments__school_class=school_class,
            enrollments__is_current=True,
        ).distinct()

        for student in students:

            status = attendance_data.get(
                student.id
            )

            if not status:
                continue

            cls.mark_attendance(
                student=student,
                attendance_date=attendance_date,
                status=status,
            )

    @classmethod
    def get_class_statistics(
        cls,
        school_class,
        attendance_date,
    ):

        students = Student.objects.filter(
            enrollments__school_class=school_class,
            enrollments__is_current=True,
        ).distinct()

        statistics = students.aggregate(
            total=Count("id"),

            present=Count(
                "attendance_records",
                filter=Q(
                    attendance_records__attendance_date=attendance_date,
                    attendance_records__status="present",
                ),
            ),

            absent=Count(
                "attendance_records",
                filter=Q(
                    attendance_records__attendance_date=attendance_date,
                    attendance_records__status="absent",
                ),
            ),

            late=Count(
                "attendance_records",
                filter=Q(
                    attendance_records__attendance_date=attendance_date,
                    attendance_records__status="late",
                ),
            ),

            excused=Count(
                "attendance_records",
                filter=Q(
                    attendance_records__attendance_date=attendance_date,
                    attendance_records__status="excused",
                ),
            ),
        )

        total = statistics["total"]

        statistics["not_marked"] = (
            total
            - (
                statistics["present"]
                + statistics["absent"]
                + statistics["late"]
                + statistics["excused"]
            )
        )

        if total:
            statistics["attendance_rate"] = round(
                (statistics["present"] / total) * 100,
                2
            )
        else:
            statistics["attendance_rate"] = 0

        return statistics

    @classmethod
    def get_student_statistics(
        cls,
        student,
        start_date=None,
        end_date=None,
    ):
        records = student.attendance_records.all()

        if start_date:
            records = records.filter(
                attendance_date__gte=start_date
            )

        if end_date:
            records = records.filter(
                attendance_date__lte=end_date
            )

        statistics = records.aggregate(
            total=Count("id"),

            present=Count(
                "id",
                filter=Q(status="present"),
            ),

            absent=Count(
                "id",
                filter=Q(status="absent"),
            ),

            late=Count(
                "id",
                filter=Q(status="late"),
            ),

            excused=Count(
                "id",
                filter=Q(status="excused"),
            ),
        )

        total = statistics["total"]

        if total:
            statistics["attendance_rate"] = round(
                (
                    statistics["present"]
                    / total
                ) * 100,
                2,
            )
        else:
            statistics["attendance_rate"] = 0

        return statistics

    @staticmethod
    def get_class_attendance_history(
        school_class,
        start_date=None,
        end_date=None,
    ):
        records = Attendance.objects.filter(
            student__enrollments__school_class=school_class,
            student__enrollments__is_current=True,
        ).select_related(
            "student",
        ).order_by(
            "-attendance_date",
            "student__first_name",
        )

        if start_date:
            records = records.filter(
                attendance_date__gte=start_date
            )

        if end_date:
            records = records.filter(
                attendance_date__lte=end_date
            )

        return records

    @staticmethod
    def get_student_attendance(student, start_date=None, end_date=None):

        records = Attendance.objects.filter(
            student=student,
        ).order_by(
            "-attendance_date",
        )

        if start_date:
            records = records.filter(
                attendance_date__gte=start_date,
            )

        if end_date:
            records = records.filter(
                attendance_date__lte=end_date,
            )

        return records

    @staticmethod
    def get_student_statistics(student, start_date=None, end_date=None):

        records = Attendance.objects.filter(
            student=student,
        )

        if start_date:
            records = records.filter(
                attendance_date__gte=start_date,
            )

        if end_date:
            records = records.filter(
                attendance_date__lte=end_date,
            )

        total = records.count()

        present = records.filter(
            status="present"
        ).count()

        absent = records.filter(
            status="absent"
        ).count()

        late = records.filter(
            status="late"
        ).count()

        excused = records.filter(
            status="excused"
        ).count()

        attendance_rate = 0

        if total:
            attendance_rate = round(
                (present / total) * 100,
                2,
            )

        return {
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
            "attendance_rate": attendance_rate,
        }