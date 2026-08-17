from django.shortcuts import get_object_or_404, render, redirect
from datetime import date
from students.models import Student

from .services import FeeService


from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages


from django.core.paginator import Paginator
from decimal import Decimal

from django.db.models import Sum, Q
from .forms import FeeInvoiceForm
from .models import FeeInvoice, Payment




def student_fees(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id,
    )

    invoices = (
        student.enrollments
        .prefetch_related(
            "fee_invoices__payments"
        )
    )
    summary = FeeService.get_student_fee_summary(
    student
    )

    fee_summaries = []

    for enrollment in invoices:

        for invoice in enrollment.fee_invoices.all():

            fee_summaries.append(
                FeeService.get_invoice_summary(
                    invoice
                )
            )

    return render(
        request,
        "fees/student_fees.html",
        {
            "student": student,
            "fee_summaries": fee_summaries,
            "fee_summary": summary,
        },
    )


def record_payment(request, invoice_id):

    invoice = get_object_or_404(
        FeeInvoice.objects.select_related(
            "enrollment__student"
        ),
        id=invoice_id,
    )

    student = invoice.enrollment.student

    if request.method == "POST":

        amount = request.POST.get("amount")
        payment_date = request.POST.get("payment_date")
        payment_method = request.POST.get("payment_method")
        reference = request.POST.get("reference", "").strip()
        remarks = request.POST.get("remarks", "").strip()

        # -------------------------
        # Validate amount
        # -------------------------

        amount = Decimal(amount)

        if amount <= Decimal("0.00"):

            raise ValueError(
                "Payment amount must be greater than zero."
            )


        if invoice.status == "cancelled":

            raise ValueError(
                "Cannot record a payment against a cancelled invoice."
            )


        balance = FeeService.get_balance(invoice)

        if amount > balance:

            raise ValueError(
                "Payment cannot be greater than "
                "the outstanding balance."
            )
        # -------------------------
        # Validate payment date
        # -------------------------

        try:

            payment_date = datetime.strptime(
                payment_date,
                "%Y-%m-%d",
            ).date()

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please provide a valid payment date.",
            )

            return redirect(
                "fees:record_payment",
                invoice_id=invoice.id,
            )

        # -------------------------
        # Record payment
        # -------------------------

        try:

            FeeService.record_payment(
                invoice=invoice,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                reference=reference,
                remarks=remarks,
            )

        except ValueError as error:

            messages.error(
                request,
                str(error),
            )

            return redirect(
                "fees:record_payment",
                invoice_id=invoice.id,
            )

        messages.success(
            request,
            "Payment recorded successfully.",
        )

        return redirect(
            "fees:student_fees",
            student_id=student.id,
        )

    summary = FeeService.get_invoice_summary(
        invoice
    )

    return render(
        request,
        "fees/record_payment.html",
        {
            "invoice": invoice,
            "student": student,
            "summary": summary,
            "today": date.today(),
        },
    )

def payment_history(request, invoice_id):

    invoice = get_object_or_404(
        FeeInvoice.objects.select_related(
            "enrollment__student"
        ),
        id=invoice_id,
    )

    student = invoice.enrollment.student

    payments = FeeService.get_payment_history(
        invoice
    )

    summary = FeeService.get_invoice_summary(
        invoice
    )

    return render(
        request,
        "fees/payment_history.html",
        {
            "invoice": invoice,
            "student": student,
            "payments": payments,
            "summary": summary,
        },
    )


def payment_receipt(request, payment_id):

    payment = get_object_or_404(
        Payment.objects.select_related(
            "invoice__enrollment__student"
        ),
        id=payment_id,
    )

    invoice = payment.invoice
    student = invoice.enrollment.student

    # Calculate total paid including this payment
    paid_before = (
        invoice.payments
        .filter(id__lt=payment.id)
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
            "student": student,
            "paid_before": paid_before,
            "balance_after": balance_after,
        },
    )

def create_invoice(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id,
    )

    enrollments = student.enrollments.all()

    if request.method == "POST":

        form = FeeInvoiceForm(
            request.POST,
        )

        form.fields["enrollment"].queryset = enrollments

        if form.is_valid():

            invoice = form.save()

            return redirect(
                "fees:student_fees",
                student_id=student.id,
            )

    else:

        form = FeeInvoiceForm()

        form.fields["enrollment"].queryset = enrollments

    return render(
        request,
        "fees/create_invoice.html",
        {
            "student": student,
            "form": form,
        },
    )
def cancel_invoice(request, invoice_id):

    invoice = get_object_or_404(
        FeeInvoice.objects.select_related(
            "enrollment__student"
        ),
        id=invoice_id,
    )

    student = invoice.enrollment.student

    if request.method != "POST":

        return redirect(
            "fees:student_fees",
            student_id=student.id,
        )

    try:

        FeeService.cancel_invoice(
            invoice
        )

    except ValueError as error:

        messages.error(
            request,
            str(error),
        )

        return redirect(
            "fees:student_fees",
            student_id=student.id,
        )

    messages.success(
        request,
        "Invoice cancelled successfully.",
    )

    return redirect(
        "fees:student_fees",
        student_id=student.id,
    )

def invoice_detail(request, invoice_id):

    invoice = get_object_or_404(
        FeeInvoice.objects.select_related(
            "enrollment__student"
        ),
        id=invoice_id,
    )

    student = invoice.enrollment.student

    summary = FeeService.get_invoice_summary(
        invoice
    )

    payments = FeeService.get_payment_history(
        invoice
    )

    return render(
        request,
        "fees/invoice_detail.html",
        {
            "invoice": invoice,
            "student": student,
            "summary": summary,
            "payments": payments,
        },
    )

def edit_invoice(request, invoice_id):

    invoice = get_object_or_404(
        FeeInvoice.objects.select_related(
            "enrollment__student"
        ),
        id=invoice_id,
    )

    student = invoice.enrollment.student

    if request.method == "POST":

        description = request.POST.get(
            "description",
            ""
        ).strip()

        amount = request.POST.get(
            "amount"
        )

        due_date = request.POST.get(
            "due_date"
        )

        if not description:

            messages.error(
                request,
                "Invoice description is required.",
            )

            return redirect(
                "fees:edit_invoice",
                invoice_id=invoice.id,
            )

        try:

            amount = Decimal(amount)

        except (InvalidOperation, TypeError):

            messages.error(
                request,
                "Please enter a valid invoice amount.",
            )

            return redirect(
                "fees:edit_invoice",
                invoice_id=invoice.id,
            )

        try:

            due_date = datetime.strptime(
                due_date,
                "%Y-%m-%d",
            ).date()

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please provide a valid due date.",
            )

            return redirect(
                "fees:edit_invoice",
                invoice_id=invoice.id,
            )

        try:

            FeeService.update_invoice(
                invoice=invoice,
                description=description,
                amount=amount,
                due_date=due_date,
            )

        except ValueError as error:

            messages.error(
                request,
                str(error),
            )

            return redirect(
                "fees:edit_invoice",
                invoice_id=invoice.id,
            )

        messages.success(
            request,
            "Invoice updated successfully.",
        )

        return redirect(
            "fees:invoice_detail",
            invoice_id=invoice.id,
        )

    paid = FeeService.get_paid_amount(
        invoice
    )

    return render(
        request,
        "fees/edit_invoice.html",
        {
            "invoice": invoice,
            "student": student,
            "paid": paid,
        },
    )
def invoice_list(request):

    invoices = (
        FeeInvoice.objects
        .select_related(
            "enrollment__student",
        )
        .prefetch_related(
            "payments",
        )
        .order_by(
            "-created_at",
        )
    )

    # -------------------------
    # Search
    # -------------------------

    search = request.GET.get(
        "search",
        "",
    ).strip()

    if search:

        invoices = invoices.filter(
            Q(
                enrollment__student__first_name__icontains=search
            )
            |
            Q(
                enrollment__student__middle_name__icontains=search
            )
            |
            Q(
                enrollment__student__last_name__icontains=search
            )
            |
            Q(
                enrollment__student__admission_number__icontains=search
            )
        )


    # -------------------------
    # Status filter
    # -------------------------

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if status:

        invoices = invoices.filter(
            status=status
        )


    # -------------------------
    # Academic year filter
    # -------------------------

    academic_year = request.GET.get(
        "academic_year",
        "",
    ).strip()

    if academic_year:

        invoices = invoices.filter(
            enrollment__academic_year=academic_year
        )


    # -------------------------
    # Pagination
    # -------------------------

    paginator = Paginator(
        invoices,
        10,
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    # -------------------------
    # Invoice summaries
    # -------------------------

    invoice_summaries = []

    for invoice in page_obj:

        invoice_summaries.append(
            FeeService.get_invoice_summary(
                invoice
            )
        )


    # -------------------------
    # Global summary
    # -------------------------

    summary = FeeService.get_fee_summary()


    # -------------------------
    # Academic years
    # -------------------------

    academic_years = (
        FeeInvoice.objects
        .values_list(
            "enrollment__academic_year",
            flat=True,
        )
        .distinct()
        .order_by(
            "-enrollment__academic_year"
        )
    )


    return render(
        request,
        "fees/invoice_list.html",
        {
            "invoice_summaries": invoice_summaries,
            "summary": summary,
            "academic_years": academic_years,
            "search": search,
            "status": status,
            "academic_year": academic_year,
            "page_obj": page_obj,
        },
    )