from django.urls import path
from . import views


app_name = "accounts"


urlpatterns = [

    path(
        "",
        views.role_home,
        name="role_home",
    ),

    path(
        "users/",
        views.user_list,
        name="user_list",
    ),
    path(
    "users/<int:user_id>/",
    views.user_detail,
    name="user_detail",
    ),

    path(
        "users/<int:user_id>/toggle-status/",
        views.toggle_user_status,
        name="toggle_user_status",
    ),
    

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "change-password/",
        views.change_password,
        name="change_password",
    ),
    path(
    "users/<int:user_id>/edit/",
    views.edit_user,
    name="edit_user",
    ),
    path(
    "users/<int:user_id>/reset-password/",
    views.reset_user_password,
    name="reset_user_password",
    ),
    path(
    "activate-parent/<uidb64>/<token>/",
    views.activate_parent,
    name="activate_parent",
    ),
    path(
    "user-management/",
    views.account_dashboard,
    name="account_dashboard"),

    path(
        "admin/",
        views.admin_home,
        name="admin_home",
    ),

    path(
        "teacher/",
        views.teacher_home,
        name="teacher_home",
    ),

    path(
        "parent/",
        views.parent_home,
        name="parent_home",
    ),

    path(
        "student/",
        views.student_home,
        name="student_home",
    ),
    path(
    "parent/child/<int:student_id>/reports/",
    views.parent_child_reports,
    name="parent_child_reports",
    ),
    path(
    "parent/report/<int:enrollment_id>/",
    views.parent_view_report,
    name="parent_view_report",
    ),
    path(
    "parent/child/<int:student_id>/attendance/",
    views.parent_child_attendance,
    name="parent_child_attendance",
    ),
    path(
    "parent/child/<int:student_id>/fees/",
    views.parent_child_fees,
    name="parent_child_fees",
    ),
    path(
    "parent/invoice/<int:invoice_id>/payments/",
    views.parent_invoice_payment_history,
    name="parent_invoice_payment_history",
    ),
    path(
    "parent/payment/<int:payment_id>/receipt/",
    views.parent_payment_receipt,
    name="parent_payment_receipt",
    ),
    path(
    "parent/profile/",
    views.parent_profile,
    name="parent_profile",
    ),
    path(
    "parent/change-password/",
    views.parent_change_password,
    name="parent_change_password",
),


    

]