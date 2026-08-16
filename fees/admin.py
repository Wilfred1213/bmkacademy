from django.contrib import admin

from .models import FeeInvoice, Payment


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "enrollment",
        "description",
        "amount",
        "due_date",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "due_date",
    )

    search_fields = (
        "enrollment__student__first_name",
        "enrollment__student__last_name",
        "enrollment__student__admission_number",
        "description",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "invoice",
        "amount",
        "payment_date",
        "payment_method",
        "reference",
        "created_at",
    )

    list_filter = (
        "payment_method",
        "payment_date",
    )

    search_fields = (
        "invoice__enrollment__student__first_name",
        "invoice__enrollment__student__last_name",
        "invoice__enrollment__student__admission_number",
        "reference",
    )