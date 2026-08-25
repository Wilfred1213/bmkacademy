from decimal import Decimal
import calendar
from django.db import transaction
from django.db.models import Sum

from .models import FeeInvoice, Payment


class FeeService:

    @staticmethod
    def get_paid_amount(invoice):
        """
        Return the total amount paid against an invoice.
        """

        total = invoice.payments.aggregate(
            total=Sum("amount")
        )["total"]

        return total or Decimal("0.00")


    @staticmethod
    def get_balance(invoice):
        """
        Return the outstanding balance on an invoice.
        """

        paid = FeeService.get_paid_amount(invoice)

        balance = invoice.amount - paid

        return max(
            balance,
            Decimal("0.00"),
        )


    @staticmethod
    def update_invoice_status(invoice):
        """
        Automatically determine the invoice status
        based on the amount paid.
        """

        paid = FeeService.get_paid_amount(invoice)

        if paid <= Decimal("0.00"):

            status = "unpaid"

        elif paid < invoice.amount:

            status = "partial"

        else:

            status = "paid"

        if invoice.status != status:

            invoice.status = status

            invoice.save(
                update_fields=["status"]
            )

        return invoice


    @staticmethod
    @transaction.atomic
    def record_payment(
        invoice,
        amount,
        payment_date,
        payment_method,
        reference="",
        remarks="",
    ):
        """
        Record a payment and automatically
        update the invoice status.
        """

        amount = Decimal(amount)

        if amount <= Decimal("0.00"):

            raise ValueError(
                "Payment amount must be greater than zero."
            )

        balance = FeeService.get_balance(invoice)

        if amount > balance:

            raise ValueError(
                "Payment cannot be greater than "
                "the outstanding balance."
            )

        payment = Payment.objects.create(
            invoice=invoice,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference=reference,
            remarks=remarks,
        )

        FeeService.update_invoice_status(
            invoice
        )

        return payment


    @staticmethod
    def get_invoice_summary(invoice):

        paid = FeeService.get_paid_amount(
            invoice
        )

        balance = FeeService.get_balance(
            invoice
        )

        return {
            "invoice": invoice,
            "amount": invoice.amount,
            "paid": paid,
            "balance": balance,
            "status": invoice.status,
        }


    @staticmethod
    def get_payment_history(invoice):

        return invoice.payments.all().order_by(
            "-payment_date",
            "-id",
        )


    @staticmethod
    def get_student_fee_summary(student):

        invoices = FeeInvoice.objects.filter(
            enrollment__student=student
        ).exclude(
            status="cancelled"
        )

        total_invoiced = (
            invoices.aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        total_paid = (
            Payment.objects.filter(
                invoice__enrollment__student=student
            )
            .exclude(
                invoice__status="cancelled"
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        outstanding = total_invoiced - total_paid

        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "outstanding": outstanding,
        }
    @staticmethod
    @transaction.atomic
    def cancel_invoice(invoice):

        if invoice is None:
            raise ValueError(
                "Invoice was not found."
            )

        paid = FeeService.get_paid_amount(invoice)

        if paid > Decimal("0.00"):
            raise ValueError(
                "An invoice with existing payments "
                "cannot be cancelled."
            )

        if invoice.status == "cancelled":
            raise ValueError(
                "This invoice is already cancelled."
            )

        invoice.status = "cancelled"

        invoice.save(
            update_fields=["status"]
        )

        return invoice

    @staticmethod
    @transaction.atomic
    def update_invoice(
        invoice,
        description,
        amount,
        due_date,
    ):
        """
        Update an invoice while protecting financial records.
        """

        paid = FeeService.get_paid_amount(invoice)

        amount = Decimal(amount)

        if amount <= Decimal("0.00"):
            raise ValueError(
                "Invoice amount must be greater than zero."
            )

        if invoice.status == "cancelled":
            raise ValueError(
                "A cancelled invoice cannot be edited."
            )

        if paid > Decimal("0.00") and amount != invoice.amount:
            raise ValueError(
                "The invoice amount cannot be changed "
                "because payments already exist."
            )

        invoice.description = description
        invoice.amount = amount
        invoice.due_date = due_date

        invoice.save(
            update_fields=[
                "description",
                "amount",
                "due_date",
            ]
        )

        return invoice

    @staticmethod
    def get_fee_summary():

        total_invoiced = (
            FeeInvoice.objects
            .exclude(status="cancelled")
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        total_paid = (
            Payment.objects
            .filter(
                invoice__status__in=[
                    "unpaid",
                    "partial",
                    "paid",
                ]
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        outstanding = (
            total_invoiced - total_paid
        )

        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "outstanding": max(
                outstanding,
                Decimal("0.00"),
            ),
        }

    @staticmethod
    def get_collection_report():

        invoices = FeeInvoice.objects.exclude(
            status="cancelled"
        )

        total_invoiced = (
            invoices.aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        total_paid = (
            Payment.objects.filter(
                invoice__status__in=[
                    "unpaid",
                    "partial",
                    "paid",
                ]
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        outstanding = (
            total_invoiced - total_paid
        )

        if total_invoiced > Decimal("0.00"):

            collection_rate = (
                total_paid / total_invoiced
            ) * Decimal("100")

        else:

            collection_rate = Decimal("0.00")


        status_breakdown = {}

        for status_code, status_label in (
            FeeInvoice.STATUS_CHOICES
        ):

            if status_code == "cancelled":
                continue

            status_invoices = invoices.filter(
                status=status_code
            )

            invoice_count = status_invoices.count()

            invoice_amount = (
                status_invoices.aggregate(
                    total=Sum("amount")
                )["total"]
                or Decimal("0.00")
            )

            status_breakdown[status_code] = {
                "label": status_label,
                "count": invoice_count,
                "amount": invoice_amount,
            }


        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "outstanding": max(
                outstanding,
                Decimal("0.00"),
            ),
            "collection_rate": collection_rate,
            "status_breakdown": status_breakdown,
        }

    @staticmethod
    def get_monthly_payment_report():

        payments = (
            Payment.objects
            .filter(
                invoice__status__in=[
                    "unpaid",
                    "partial",
                    "paid",
                ]
            )
            .values(
                "payment_date__year",
                "payment_date__month",
            )
            .annotate(
                total=Sum("amount")
            )
            .order_by(
                "payment_date__year",
                "payment_date__month",
            )
        )

        

        report = []

        for item in payments:

            year = item[
                "payment_date__year"
            ]

            month = item[
                "payment_date__month"
            ]

            report.append(
                {
                    "year": year,
                    "month": month,
                    "month_name": calendar.month_name[
                        month
                    ],
                    "total": item[
                        "total"
                    ],
                }
            )

        return report

    @staticmethod
    def get_outstanding_fees():
        invoices = (
            FeeInvoice.objects
            .exclude(status="cancelled")
            .select_related(
                "enrollment__student",
            )
            .prefetch_related(
                "payments",
            )
        )

        outstanding = []

        for invoice in invoices:

            paid = FeeService.get_paid_amount(
                invoice
            )

            balance = FeeService.get_balance(
                invoice
            )

            if balance > Decimal("0.00"):

                outstanding.append(
                    {
                        "invoice": invoice,
                        "student": invoice.enrollment.student,
                        "enrollment": invoice.enrollment,
                        "amount": invoice.amount,
                        "paid": paid,
                        "balance": balance,
                        "status": invoice.status,
                    }
                )

        return outstanding

    @staticmethod
    def get_class_fee_summary(
        school_class,
        academic_year,
    ):

        invoices = FeeInvoice.objects.filter(
            enrollment__school_class=school_class,
            enrollment__academic_year=academic_year,
        ).exclude(
            status="cancelled"
        )

        total_invoiced = (
            invoices.aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        total_paid = (
            Payment.objects.filter(
                invoice__in=invoices
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        outstanding = (
            total_invoiced - total_paid
        )

        if total_invoiced > Decimal("0.00"):

            collection_rate = (
                total_paid / total_invoiced
            ) * Decimal("100")

        else:

            collection_rate = Decimal("0.00")

        student_count = (
            invoices.values(
                "enrollment__student"
            ).distinct().count()
        )

        return {
            "school_class": school_class,
            "academic_year": academic_year,
            "student_count": student_count,
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "outstanding": max(
                outstanding,
                Decimal("0.00"),
            ),
            "collection_rate": collection_rate,
        }

    @staticmethod
    def get_class_student_fee_summary(
        school_class,
        academic_year,
    ):

        enrollments = (
            school_class.enrollments
            .filter(
                academic_year=academic_year,
            )
            .select_related(
                "student",
            )
            .prefetch_related(
                "fee_invoices__payments",
            )
        )

        student_summaries = []

        for enrollment in enrollments:

            invoices = (
                enrollment.fee_invoices
                .exclude(
                    status="cancelled"
                )
            )

            # -------------------------
            # Total invoiced
            # -------------------------

            total_invoiced = (
                invoices.aggregate(
                    total=Sum("amount")
                )["total"]
                or Decimal("0.00")
            )

            # -------------------------
            # Total paid
            # -------------------------

            total_paid = Decimal("0.00")

            for invoice in invoices:

                total_paid += (
                    FeeService.get_paid_amount(
                        invoice
                    )
                )

            # -------------------------
            # Outstanding balance
            # -------------------------

            outstanding = (
                total_invoiced
                - total_paid
            )

            if outstanding < Decimal("0.00"):

                outstanding = Decimal(
                    "0.00"
                )

            # -------------------------
            # Payment status
            # -------------------------

            if total_paid <= Decimal("0.00"):

                status = "unpaid"

            elif outstanding > Decimal("0.00"):

                status = "partial"

            else:

                status = "paid"

            # -------------------------
            # Outstanding percentage
            # -------------------------

            if total_invoiced > Decimal("0.00"):

                outstanding_percentage = (
                    outstanding
                    / total_invoiced
                ) * Decimal("100")

            else:

                outstanding_percentage = Decimal(
                    "0.00"
                )

            # -------------------------
            # Risk level
            # -------------------------

            if status == "paid":

                risk_level = "paid"

            elif outstanding_percentage > Decimal(
                "60"
            ):

                risk_level = "high"

            elif outstanding_percentage > Decimal(
                "30"
            ):

                risk_level = "medium"

            else:

                risk_level = "low"

            # -------------------------
            # Add student summary
            # -------------------------

            student_summaries.append(
                {
                    "student": enrollment.student,
                    "enrollment": enrollment,

                    "total_invoiced": total_invoiced,

                    "total_paid": total_paid,

                    "outstanding": outstanding,

                    "outstanding_percentage":
                        outstanding_percentage,

                    "status": status,

                    "risk_level": risk_level,
                }
            )

        # =================================
        # THIS IS OUTSIDE THE FOR LOOP
        # =================================

        student_summaries.sort(
            key=lambda item: item["outstanding"],
            reverse=True,
        )

        return student_summaries

    @staticmethod
    def get_fee_risk_summary(student_summaries):

        risk_summary = {
            "paid": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for item in student_summaries:

            risk_level = item["risk_level"]

            if risk_level in risk_summary:

                risk_summary[risk_level] += 1

        return risk_summary

    @staticmethod
    def get_filtered_class_student_fee_summary(
        school_class,
        academic_year,
        risk_filter=None,
        search="",
    ):

        student_summaries = (
            FeeService.get_class_student_fee_summary(
                school_class=school_class,
                academic_year=academic_year,
            )
        )

        # -----------------------------
        # Risk filter
        # -----------------------------

        if risk_filter in [
            "high",
            "medium",
            "low",
            "paid",
        ]:

            student_summaries = [
                item
                for item in student_summaries
                if item["risk_level"] == risk_filter
            ]

        # -----------------------------
        # Search filter
        # -----------------------------

        if search:

            search_lower = search.lower()

            filtered_summaries = []

            for item in student_summaries:

                student = item["student"]

                full_name = (
                    f"{student.first_name} "
                    f"{student.middle_name or ''} "
                    f"{student.last_name}"
                ).lower()

                full_name = " ".join(
                    full_name.split()
                )

                if (
                    search_lower in full_name
                    or search_lower
                    in student.admission_number.lower()
                ):

                    filtered_summaries.append(
                        item
                    )

            student_summaries = filtered_summaries

        return student_summaries