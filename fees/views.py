from django.shortcuts import get_object_or_404, render, redirect
from datetime import date
from students.models import Student

from .services import FeeService

from django.http import HttpResponse

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from academics.models import SchoolClass

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

def fee_report(request):

    report = FeeService.get_collection_report()

    return render(
        request,
        "fees/fee_report.html",
        {
            "report": report,
        },
    )

def monthly_payment_report(request):

    monthly_report = (
        FeeService.get_monthly_payment_report()
    )

    chart_labels = [
        f"{item['month_name']} {item['year']}"
        for item in monthly_report
    ]

    chart_values = [
        float(item["total"])
        for item in monthly_report
    ]

    return render(
        request,
        "fees/monthly_payment_report.html",
        {
            "monthly_report": monthly_report,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
        },
    )

def outstanding_fees(request):

    class_id = request.GET.get("class_id")
    academic_year = request.GET.get("academic_year")
    search = request.GET.get("search", "").strip()

    outstanding = FeeService.get_outstanding_fees()

    if class_id:
        outstanding = [
            item
            for item in outstanding
            if str(item["enrollment"].school_class.id) == class_id
        ]

    if academic_year:
        outstanding = [
            item
            for item in outstanding
            if str(item["enrollment"].academic_year) == academic_year
        ]

    if search:
        search_lower = search.lower()

        outstanding = [
            item
            for item in outstanding
            if (
                search_lower
                in (
                    f"{item['student'].first_name} "
                    f"{item['student'].middle_name or ''} "
                    f"{item['student'].last_name}"
                ).lower()
                or search_lower
                in item["student"].admission_number.lower()
            )
        ]

    total_outstanding = sum(
        item["balance"]
        for item in outstanding
    )

    school_classes = SchoolClass.objects.all().order_by("name")

    academic_years = (
        FeeInvoice.objects
        .values_list(
            "enrollment__academic_year",
            flat=True,
        )
        .distinct()
        .order_by("enrollment__academic_year")
    )

    return render(
        request,
        "fees/outstanding_fees.html",
        {
            "outstanding": outstanding,
            "total_outstanding": total_outstanding,
            "school_classes": school_classes,
            "academic_years": academic_years,
            "selected_class": class_id,
            "selected_academic_year": academic_year,
            "search": search,
        },
    )

def class_fee_summary(request):

    class_id = request.GET.get("class_id")
    academic_year = request.GET.get("academic_year")
    risk_filter = request.GET.get("risk")

    search = request.GET.get(
        "search",
        ""
    ).strip()

    school_classes = SchoolClass.objects.all().order_by(
        "name"
    )

    academic_years = (
        FeeInvoice.objects
        .values_list(
            "enrollment__academic_year",
            flat=True,
        )
        .distinct()
        .order_by(
            "enrollment__academic_year"
        )
    )

    risk_summary = {
    "paid": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    }
    
    summary = None
    student_summaries = []
    student_page=None


    if class_id and academic_year:

        school_class = get_object_or_404(
            SchoolClass,
            id=class_id,
        )

        summary = (
            FeeService.get_class_fee_summary(
                school_class=school_class,
                academic_year=academic_year,
            )
        )

        # ---------------------------------
        # Get ALL students for risk summary
        # ---------------------------------

        all_student_summaries = (
            FeeService.get_class_student_fee_summary(
                school_class=school_class,
                academic_year=academic_year,
            )
        )


        # ---------------------------------
        # Calculate risk counts
        # ---------------------------------

        risk_summary = (
            FeeService.get_fee_risk_summary(
                all_student_summaries
            )
        )


        # ---------------------------------
        # Get filtered students for table
        # ---------------------------------

        student_summaries = (
            FeeService.get_filtered_class_student_fee_summary(
                school_class=school_class,
                academic_year=academic_year,
                risk_filter=risk_filter,
                search=search,
            )
        )
        paginator = Paginator(
            student_summaries,
            10,
        )

        page_number = request.GET.get(
            "page"
        )

        student_page = paginator.get_page(
            page_number
        )
    chart_labels = []
    chart_values = []

    if summary:

        chart_labels = [
            "Total Invoiced",
            "Total Paid",
            "Outstanding",
        ]

        chart_values = [
            float(summary["total_invoiced"]),
            float(summary["total_paid"]),
            float(summary["outstanding"]),
        ]
    return render(
        request,
        "fees/class_fee_summary.html",
        {
            "summary": summary,
            "school_classes": school_classes,
            "academic_years": academic_years,
            "selected_class": class_id,
            "selected_academic_year": academic_year,
            "student_summaries": student_summaries,
            "risk_summary": risk_summary,
            "risk_filter": risk_filter,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
            "search": search,
            "student_page": student_page,
        },
    )

def export_class_fee_summary(request):

    class_id = request.GET.get(
        "class_id"
    )

    academic_year = request.GET.get(
        "academic_year"
    )

    risk_filter = request.GET.get(
        "risk"
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()


    if not class_id or not academic_year:

        messages.error(
            request,
            "Please select a class and academic year first.",
        )

        return redirect(
            "fees:class_fee_summary"
        )


    school_class = get_object_or_404(
        SchoolClass,
        id=class_id,
    )


    student_summaries = (
        FeeService.get_filtered_class_student_fee_summary(
            school_class=school_class,
            academic_year=academic_year,
            risk_filter=risk_filter,
            search=search,
        )
    )

    # -----------------------------
    # Create workbook
    # -----------------------------

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Class Fee Summary"


    # -----------------------------
    # Report title
    # -----------------------------

    worksheet["A1"] = (
        f"Class Fee Summary - "
        f"{school_class}"
    )

    worksheet["A2"] = (
        f"Academic Year: {academic_year}"
    )


    if risk_filter:

        worksheet["A3"] = (
            f"Risk Filter: "
            f"{risk_filter.title()}"
        )


    if search:

        worksheet["A4"] = (
            f"Search: {search}"
        )


    # -----------------------------
    # Table headers
    # -----------------------------

    headers = [

        "#",

        "Student",

        "Admission Number",

        "Total Invoiced",

        "Total Paid",

        "Outstanding",

        "Outstanding %",

        "Status",

        "Risk Level",

    ]


    start_row = 6


    for column_number, header in enumerate(
        headers,
        start=1,
    ):

        cell = worksheet.cell(
            row=start_row,
            column=column_number,
        )

        cell.value = header

        cell.font = Font(
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center"
        )


    # -----------------------------
    # Student rows
    # -----------------------------

    row_number = start_row + 1


    for index, item in enumerate(
        student_summaries,
        start=1,
    ):

        student = item["student"]


        worksheet.cell(
            row=row_number,
            column=1,
            value=index,
        )


        worksheet.cell(
            row=row_number,
            column=2,
            value=(
                f"{student.first_name} "
                f"{student.last_name}"
            ),
        )


        worksheet.cell(
            row=row_number,
            column=3,
            value=student.admission_number,
        )


        worksheet.cell(
            row=row_number,
            column=4,
            value=float(
                item["total_invoiced"]
            ),
        )


        worksheet.cell(
            row=row_number,
            column=5,
            value=float(
                item["total_paid"]
            ),
        )


        worksheet.cell(
            row=row_number,
            column=6,
            value=float(
                item["outstanding"]
            ),
        )


        worksheet.cell(
            row=row_number,
            column=7,
            value=float(
                item[
                    "outstanding_percentage"
                ]
            ),
        )


        worksheet.cell(
            row=row_number,
            column=8,
            value=item["status"],
        )


        worksheet.cell(
            row=row_number,
            column=9,
            value=item["risk_level"],
        )


        row_number += 1


    # -----------------------------
    # Format currency columns
    # -----------------------------

    for row in range(
        start_row + 1,
        row_number,
    ):

        for column in [4, 5, 6]:

            worksheet.cell(
                row=row,
                column=column,
            ).number_format = (
                '₦#,##0.00'
            )


        worksheet.cell(
            row=row,
            column=7,
        ).number_format = (
            '0.0"%"'
        )


    # -----------------------------
    # Adjust column widths
    # -----------------------------

    column_widths = {

        "A": 8,

        "B": 30,

        "C": 25,

        "D": 18,

        "E": 18,

        "F": 18,

        "G": 15,

        "H": 15,

        "I": 15,

    }


    for column, width in column_widths.items():

        worksheet.column_dimensions[
            column
        ].width = width


    # -----------------------------
    # Create response
    # -----------------------------

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


    filename = (
        f"{school_class}_"
        f"{academic_year}_"
        f"fee_summary.xlsx"
    )


    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="{filename}"'
    )


    workbook.save(
        response
    )


    return response