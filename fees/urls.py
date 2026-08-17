from django.urls import path

from . import views


app_name = "fees"


urlpatterns = [

    path(
        "student/<int:student_id>/",
        views.student_fees,
        name="student_fees",
    ),
    path(
        "payment/<int:invoice_id>/",
        views.record_payment,
        name="record_payment",
    ),
    path(
    "payment-history/<int:invoice_id>/",
    views.payment_history,
    name="payment_history",
    ),
    path(
    "payment/<int:payment_id>/receipt/",
    views.payment_receipt,
    name="payment_receipt",
    ),
    path(
    "student/<int:student_id>/invoice/create/",
    views.create_invoice,
    name="create_invoice",
    ),
    path(
        "invoice/<int:invoice_id>/cancel/",
        views.cancel_invoice,
        name="cancel_invoice",
    ),
    path(
    "invoice/<int:invoice_id>/",
    views.invoice_detail,
    name="invoice_detail",
    ),
    path(
    "invoice/<int:invoice_id>/edit/",
    views.edit_invoice,
    name="edit_invoice",
    ),
    path(
    "",
    views.invoice_list,
    name="invoice_list",
),


]