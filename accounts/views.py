
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import logout
from .decorators import role_required
from django.contrib.auth.decorators import login_required
from .services import UserService
from .models import User, ParentProfile
from students.models import Enrollment
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from reports.services import ReportService
from results.services import ResultService
from django.urls import reverse
from students.models import Student
from teachers.models import Teacher
from admissions.models import AdmissionApplication
from results.models import StudentTermReport
from django.core.exceptions import PermissionDenied
from decimal import Decimal
from results.models import StudentTermReport
from attendance.services import AttendanceService
from fees.services import FeeService, FeeInvoice
from fees.models import Payment
from django.db.models import Sum
from notifications.services import NotificationService
from .forms import ParentProfileForm
from django.contrib.auth.forms import PasswordChangeForm

@login_required
@role_required("admin")
def account_dashboard(request):

    users = User.objects.all().order_by(
        "first_name",
        "last_name",
    )

    context = {
        "users": users,
        "total_users": users.count(),
        "total_admins": users.filter(
            role="admin"
        ).count(),
        "total_teachers": users.filter(
            role="teacher"
        ).count(),
        "total_parents": users.filter(
            role="parent"
        ).count(),
        "total_students": users.filter(
            role="student"
        ).count(),
    }

    return render(
        request,
        "accounts/account_dashboard.html",
        context,
    )

def login_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:role_home")

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST,
        )

        if form.is_valid():

            user = form.get_user()

            login(
                request,
                user,
            )

            if user.must_change_password:
                return redirect(
                    "accounts:change_password"
                )

            return redirect(
                "accounts:role_home"
            )

    else:

        form = AuthenticationForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
        },
    )

def logout_view(request):

    if request.method == "POST":

        logout(request)

        return redirect("accounts:login")

    return redirect("accounts:login")


@login_required
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST,
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user,
            )

            user.must_change_password = False

            user.save(
                update_fields=[
                    "must_change_password",
                ]
            )

            messages.success(
                request,
                "Your password has been changed successfully.",
            )

            
            return redirect(
                "accounts:role_home"
            )

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form,
        },
    )

@login_required
@role_required("admin")
def user_list(request):

    users = User.objects.all().order_by(
        "first_name",
        "last_name",
    )

    context = {
        "users": users,
    }

    return render(
        request,
        "accounts/user_list.html",
        context,
    )

@login_required
@role_required("admin")
def toggle_user_status(request, user_id):

    user = get_object_or_404(User, id=user_id)

    # Prevent admin from accidentally disabling their own account
    if user == request.user:
        messages.error(
            request,
            "You cannot deactivate your own account.",
        )
        return redirect("accounts:user_list")

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    if user.is_active:
        messages.success(
            request,
            f"{user.get_full_name() or user.username} has been activated.",
        )
    else:
        messages.success(
            request,
            f"{user.get_full_name() or user.username} has been deactivated.",
        )

    return redirect("accounts:user_list")

@login_required
@role_required("admin")
def user_detail(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id,
    )

    return render(
        request,
        "accounts/user_detail.html",
        {
            "user_account": user,
        },
    )

@login_required
@role_required("admin")
def edit_user(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id,
    )

    if request.method == "POST":

        user.first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        user.last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        user.username = request.POST.get(
            "username",
            ""
        ).strip()

        user.email = request.POST.get(
            "email",
            ""
        ).strip()

        user.role = request.POST.get(
            "role"
        )

        user.save()

        messages.success(
            request,
            "User account updated successfully.",
        )

        return redirect(
            "accounts:user_detail",
            user_id=user.id,
        )

    return render(
        request,
        "accounts/edit_user.html",
        {
            "user_account": user,
        },
    )

@login_required
@role_required("admin")
def reset_user_password(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id,
    )

    if user == request.user:
        messages.error(
            request,
            "You cannot reset your own password from here.",
        )
        return redirect(
            "accounts:user_detail",
            user_id=user.id,
        )

    if request.method != "POST":
        return redirect(
            "accounts:user_detail",
            user_id=user.id,
        )

    temporary_password = UserService.reset_password(
        user
    )

    messages.success(
        request,
        f"Temporary password generated for "
        f"{user.get_full_name() or user.username}: "
        f"{temporary_password}",
    )

    return redirect(
        "accounts:user_detail",
        user_id=user.id,
    )

def activate_parent(request, uidb64, token):

    User = get_user_model()

    try:

        uid = urlsafe_base64_decode(
            uidb64
        ).decode()

        user = User.objects.get(
            pk=uid,
            role="parent",
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):

        user = None

    if user is None:

        messages.error(
            request,
            "This activation link is invalid.",
        )

        return redirect(
            "accounts:login"
        )

    if not default_token_generator.check_token(
        user,
        token,
    ):

        messages.error(
            request,
            "This activation link is invalid or has expired.",
        )

        return redirect(
            "accounts:login"
        )

    if request.method == "POST":

        password1 = request.POST.get(
            "password1",
            ""
        )

        password2 = request.POST.get(
            "password2",
            ""
        )

        if not password1 or not password2:

            messages.error(
                request,
                "Please enter and confirm your password.",
            )

        elif password1 != password2:

            messages.error(
                request,
                "The passwords do not match.",
            )

        elif len(password1) < 8:

            messages.error(
                request,
                "Password must be at least 8 characters.",
            )

        else:

            user.set_password(
                password1
            )

            user.is_active = True

            user.must_change_password = False

            user.save(
                update_fields=[
                    "password",
                    "is_active",
                    "must_change_password",
                ]
            )

            messages.success(
                request,
                "Your account has been activated. "
                "You can now log in.",
            )

            return redirect(
                "accounts:login"
            )

    return render(
        request,
        "accounts/activate_parent.html",
        {
            "user": user,
        },
    )

@login_required
def role_home(request):

    if request.user.role == "admin":
        return redirect("accounts:admin_home")

    if request.user.role == "teacher":
        return redirect("accounts:teacher_home")

    if request.user.role == "parent":
        return redirect("accounts:parent_home")

    if request.user.role == "student":
        return redirect("accounts:student_home")

    return redirect("accounts:home")

@login_required
@role_required("admin")
def admin_home(request):

    
    context = {
        "total_users": User.objects.count(),

        "total_students": Student.objects.count(),

        "total_teachers": Teacher.objects.count(),

        "pending_admissions": AdmissionApplication.objects.filter(
            status="pending"
        ).count(),

        "approved_admissions": AdmissionApplication.objects.filter(
            status="approved"
        ).count(),

    }

    return render(
        request,
        "accounts/admin_home.html",
        context,
    )

@login_required
@role_required("teacher")
def teacher_home(request):
    from teachers.models import Teacher, TeachingAssignment, ClassTeacherAssignment

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
        is_active=True,
    )

    assignments = TeachingAssignment.objects.filter(
        teacher=teacher
    ).select_related(
        "class_subject",
        "class_subject__school_class",
        "class_subject__subject",
        "academic_year",
    )

    class_teacher_assignments = ClassTeacherAssignment.objects.filter(
        teacher=teacher,
        is_active=True,
    ).select_related(
        "school_class",
        "academic_year",
    )

    return render(
        request,
        "accounts/teacher_home.html",
        {
            "teacher": teacher,
            "assignments": assignments,
            "class_teacher_assignments": class_teacher_assignments,
        },
    )

@login_required
@role_required("parent")
def parent_home(request):
    parent_profile = get_object_or_404(
        ParentProfile,
        user=request.user,
    )

    children = (
        parent_profile.children
        .prefetch_related("enrollments")
        .order_by("first_name", "last_name")
    )

    for child in children:

        # Get current enrollment
        enrollment = (
            child.enrollments
            .filter(is_current=True)
            .select_related(
                "academic_year",
                "term",
                "school_class",
            )
            .order_by(
                "-academic_year__start_date",
                "-term__start_date",
            )
            .first()
        )

        child.current_enrollment = enrollment

        # Attendance summary
        if enrollment:
            child.attendance_statistics = (
                AttendanceService.get_student_statistics(
                    student=child,
                    start_date=enrollment.term.start_date,
                    end_date=enrollment.term.end_date,
                )
            )
        else:
            child.attendance_statistics = None

        # Published reports
        child.published_report_count = (
            StudentTermReport.objects.filter(
                enrollment__student=child,
                is_published=True,
            ).count()
        )

        # Fee summary
        if enrollment:
            child.fee_summary = FeeService.get_enrollment_fee_summary(
                enrollment=enrollment
            )
        else:
            child.fee_summary = {
                "total_invoiced": Decimal("0.00"),
                "total_paid": Decimal("0.00"),
                "outstanding": Decimal("0.00"),
            }

    # Parent notifications
    notifications = (
        NotificationService
        .get_user_notifications(request.user)
        .order_by("-created_at")[:1]
    )

    unread_notification_count = (
        NotificationService
        .get_unread_count(request.user)
    )

    return render(
        request,
        "accounts/parent_home.html",
        {
            "parent_profile": parent_profile,
            "children": children,
            "notifications": notifications,
            "unread_notification_count": unread_notification_count,
        },
    )
@login_required
@role_required("student")
def student_home(request):

    return render(
        request,
        "accounts/student_home.html",

    )

@login_required
@role_required("parent")
def parent_child_reports(request, student_id):

    parent_profile = get_object_or_404(
        ParentProfile,
        user=request.user,
    )

    # Make sure this student actually belongs
    # to the logged-in parent.
    child = get_object_or_404(
        parent_profile.children.all(),
        id=student_id,
    )

    # Get this child's published reports.
    reports = (
        StudentTermReport.objects
        .filter(
            enrollment__student=child,
            is_published=True,
        )
        .select_related(
            "enrollment",
            "enrollment__academic_year",
            "enrollment__term",
            "enrollment__school_class",
        )
        .order_by(
            "-enrollment__academic_year__start_date",
            "-enrollment__term__start_date",
        )
    )

    return render(
        request,
        "accounts/parent_child_reports.html",
        {
            "parent_profile": parent_profile,
            "child": child,
            "reports": reports,
        },
    )
@login_required
@role_required("parent")
def parent_child_fees(request, student_id):

    parent_profile = get_object_or_404(
        ParentProfile,
        user=request.user,
    )

    # Make sure this student actually belongs
    # to the logged-in parent.
    child = get_object_or_404(
        parent_profile.children.all(),
        id=student_id,
    )

    # Get the child's current enrollment.
    enrollment = (
        Enrollment.objects
        .filter(
            student=child,
            is_current=True,
        )
        .select_related(
            "academic_year",
            "term",
            "school_class",
        )
        .order_by(
            "-academic_year__start_date",
            "-term__start_date",
        )
        .first()
    )

    if not enrollment:
        return render(
            request,
            "accounts/parent_child_fees.html",
            {
                "child": child,
                "enrollment": None,
                "invoices": [],
                "fee_summary": None,
            },
        )
    
    # Get invoices belonging to this enrollment.
    invoices = (
        FeeInvoice.objects
        .filter(
            enrollment=enrollment,
        )
        .exclude(
            status="cancelled",
        )
        .prefetch_related(
            "payments",
        )
        .order_by(
            "due_date",
            "id",
        )
    )

    # Current enrollment fee summary.
    fee_summary = FeeService.get_enrollment_fee_summary(
        enrollment=enrollment,
    )

    return render(
        request,
        "accounts/parent_child_fees.html",
        {
            "child": child,
            "enrollment": enrollment,
            "invoices": invoices,
            "fee_summary": fee_summary,
        },
    )

@login_required
@role_required("parent")
def parent_view_report(request, enrollment_id):

    # =================================
    # GET PARENT PROFILE
    # =================================

    parent_profile = get_object_or_404(
        ParentProfile,
        user=request.user,
    )

    # =================================
    # GET ENROLLMENT
    # =================================

    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            "student",
            "academic_year",
            "term",
            "school_class",
        ),
        id=enrollment_id,
    )

    # =================================
    # PARENT ACCESS CHECK
    # =================================

    if not parent_profile.children.filter(
        id=enrollment.student_id
    ).exists():

        raise PermissionDenied

    # =================================
    # PUBLISHED REPORT CHECK
    # =================================

    get_object_or_404(
        StudentTermReport,
        enrollment=enrollment,
        is_published=True,
    )

    # =================================
    # GET COMPLETE REPORT
    # =================================

    report = (
        ResultService
        .get_complete_student_result(
            enrollment=enrollment,
            include_position=False,
        )
    )

    # =================================
    # RENDER REPORT CARD
    # =================================

    return render(
        request,
        "results/student_report_card.html",
        {
            "report": report,
            "back_url": reverse(
                "accounts:parent_child_reports",
                args=[enrollment.student.id],
            ),
            "from_parent": True,
        }
    )

@login_required
@role_required("parent")
def parent_child_attendance(request, student_id):

    # =================================
    # GET PARENT PROFILE
    # =================================

    parent_profile = get_object_or_404(
        ParentProfile,
        user=request.user,
    )

    # =================================
    # VERIFY CHILD BELONGS TO PARENT
    # =================================

    child = get_object_or_404(
        parent_profile.children.all(),
        id=student_id,
    )

    # =================================
    # GET CHILD'S CURRENT ENROLLMENT
    # =================================

    enrollment = (
        Enrollment.objects
        .filter(
            student=child,
            is_current=True,
        )
        .select_related(
            "academic_year",
            "term",
            "school_class",
        )
        .first()
    )

    # =================================
    # NO CURRENT ENROLLMENT
    # =================================

    if not enrollment:
        return render(
            request,
            "accounts/parent_child_attendance.html",
            {
                "child": child,
                "enrollment": None,
                "records": [],
                "statistics": None,
            },
        )

    # =================================
    # TERM DATE RANGE
    # =================================

    start_date = enrollment.term.start_date
    end_date = enrollment.term.end_date

    # =================================
    # GET ATTENDANCE
    # =================================

    records = AttendanceService.get_student_attendance(
        student=child,
        start_date=start_date,
        end_date=end_date,
    )

    statistics = AttendanceService.get_student_statistics(
        student=child,
        start_date=start_date,
        end_date=end_date,
    )

    # =================================
    # RENDER
    # =================================

    return render(
        request,
        "accounts/parent_child_attendance.html",
        {
            "child": child,
            "enrollment": enrollment,
            "records": records,
            "statistics": statistics,
        },
    )

@login_required
@role_required("parent")
def parent_invoice_payment_history(request, invoice_id):

    parent_profile = get_object_or_404(
        ParentProfile,
        user=request.user,
    )

    invoice = get_object_or_404(
        FeeInvoice.objects.select_related(
            "enrollment",
            "enrollment__student",
            "enrollment__academic_year",
            "enrollment__term",
            "enrollment__school_class",
        ),
        id=invoice_id,
    )

    # Make sure this invoice belongs to one of the parent's children
    if not parent_profile.children.filter(
        id=invoice.enrollment.student_id
    ).exists():
        raise PermissionDenied

    payments = FeeService.get_payment_history(
        invoice=invoice,
    )

    invoice_summary = FeeService.get_invoice_summary(
        invoice=invoice,
    )

    return render(
        request,
        "accounts/parent_payment_history.html",
        {
            "parent_profile": parent_profile,
            "invoice": invoice,
            "payments": payments,
            "invoice_summary": invoice_summary,
            "child": invoice.enrollment.student,
        },
    )

@login_required
@role_required("parent")
def parent_payment_receipt(request, payment_id):

    parent_profile = get_object_or_404(
        ParentProfile,
        user=request.user,
    )

    payment = get_object_or_404(
        Payment.objects.select_related(
            "invoice",
            "invoice__enrollment",
            "invoice__enrollment__student",
        ),
        id=payment_id,
    )

    child = payment.invoice.enrollment.student

    # Make sure this payment belongs to one of the parent's children
    if not parent_profile.children.filter(
        id=child.id
    ).exists():
        raise PermissionDenied

    invoice = payment.invoice

    # Calculate total paid before this payment
    paid_before = (
        invoice.payments
        .filter(
            id__lt=payment.id
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    balance_after = invoice.amount - (
        paid_before + payment.amount
    )

    return render(
        request,
        "fees/payment_receipt.html",
        {
            "payment": payment,
            "invoice": invoice,
            "student": child,
            "paid_before": paid_before,
            "balance_after": balance_after,
            "from_parent": True,
        },
    )

@login_required
@role_required("parent")
def parent_profile(request):

    parent_profile = get_object_or_404(
        ParentProfile,
        user=request.user,
    )

    if request.method == "POST":

        form = ParentProfileForm(
            request.POST,
            instance=parent_profile,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your profile has been updated successfully.",
            )

            return redirect(
                "accounts:parent_profile"
            )

    else:

        form = ParentProfileForm(
            instance=parent_profile,
        )

    children_count = parent_profile.children.count()

    return render(
        request,
        "accounts/parent_profile.html",
        {
            "parent_profile": parent_profile,
            "children_count": children_count,
            "form": form,
        },
    )

@login_required
@role_required("parent")
def parent_change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            user=request.user,
            data=request.POST,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your password has been changed successfully.",
            )

            return redirect(
                "accounts:parent_profile"
            )

    else:

        form = PasswordChangeForm(
            user=request.user,
        )

    return render(
        request,
        "accounts/parent_change_password.html",
        {
            "form": form,
        },
    )