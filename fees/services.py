from decimal import Decimal

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
            ).aggregate(
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
        """
        Cancel an invoice.

        A cancelled invoice cannot receive new payments.
        Existing payment records are preserved.
        """

        if invoice.status == "cancelled":
            raise ValueError(
                "This invoice is already cancelled."
            )

        paid = FeeService.get_paid_amount(invoice)

        if paid > Decimal("0.00"):
            raise ValueError(
                "An invoice with existing payments "
                "cannot be cancelled."
            )

        invoice.status = "cancelled"

        invoice.save(
            update_fields=["status"]
        )

        return invoice


# from decimal import Decimal

# from django.db import transaction
# from django.db.models import Sum

# from .models import FeeInvoice, Payment


# class FeeService:

#     @staticmethod
#     def get_paid_amount(invoice):
#         """
#         Return the total amount paid against an invoice.
#         """

#         total = invoice.payments.aggregate(
#             total=Sum("amount")
#         )["total"]

#         return total or Decimal("0.00")


#     @staticmethod
#     def get_balance(invoice):
#         """
#         Return the outstanding balance on an invoice.
#         """

#         paid = FeeService.get_paid_amount(invoice)

#         balance = invoice.amount - paid

#         return max(
#             balance,
#             Decimal("0.00"),
#         )


#     @staticmethod
#     def update_invoice_status(invoice):
#         """
#         Automatically determine the invoice status
#         based on the amount paid.
#         """

#         paid = FeeService.get_paid_amount(invoice)

#         if paid <= Decimal("0.00"):

#             status = "unpaid"

#         elif paid < invoice.amount:

#             status = "partial"

#         else:

#             status = "paid"

#         if invoice.status != status:

#             invoice.status = status

#             invoice.save(
#                 update_fields=["status"]
#             )

#         return invoice


#     @staticmethod
#     @transaction.atomic
#     def record_payment(
#         invoice,
#         amount,
#         payment_date,
#         payment_method,
#         reference="",
#         remarks="",
#     ):
#         """
#         Record a payment and automatically
#         update the invoice status.
#         """

#         amount = Decimal(amount)

#         if amount <= Decimal("0.00"):
#             raise ValueError(
#                 "Payment amount must be greater than zero."
#             )

#         balance = FeeService.get_balance(invoice)

#         if amount > balance:
#             raise ValueError(
#                 "Payment cannot be greater than "
#                 "the outstanding balance."
#             )

#         payment = Payment.objects.create(
#             invoice=invoice,
#             amount=amount,
#             payment_date=payment_date,
#             payment_method=payment_method,
#             reference=reference,
#             remarks=remarks,
#         )

#         FeeService.update_invoice_status(
#             invoice
#         )

#         return payment


#     @staticmethod
#     def get_invoice_summary(invoice):

#         paid = FeeService.get_paid_amount(
#             invoice
#         )

#         balance = FeeService.get_balance(
#             invoice
#         )

#         return {
#             "invoice": invoice,
#             "amount": invoice.amount,
#             "paid": paid,
#             "balance": balance,
#             "status": invoice.status,
#         }

#     @staticmethod
#     def get_payment_history(invoice):
#         return invoice.payments.all().order_by(
#             "-payment_date",
#             "-id",
#         )

 
# class FeeService:

#     @staticmethod
#     def get_paid_amount(invoice):
#         """
#         Return the total amount paid against an invoice.
#         """

#         total = invoice.payments.aggregate(
#             total=Sum("amount")
#         )["total"]

#         return total or Decimal("0.00")


#     @staticmethod
#     def get_balance(invoice):
#         """
#         Return the outstanding balance on an invoice.
#         """

#         paid = FeeService.get_paid_amount(invoice)

#         balance = invoice.amount - paid

#         return max(
#             balance,
#             Decimal("0.00"),
#         )


#     @staticmethod
#     def update_invoice_status(invoice):
#         """
#         Automatically determine the invoice status
#         based on the amount paid.
#         """

#         paid = FeeService.get_paid_amount(invoice)

#         if paid <= Decimal("0.00"):

#             status = "unpaid"

#         elif paid < invoice.amount:

#             status = "partial"

#         else:

#             status = "paid"

#         if invoice.status != status:

#             invoice.status = status

#             invoice.save(
#                 update_fields=["status"]
#             )

#         return invoice


#     @staticmethod
#     @transaction.atomic
#     def record_payment(
#         invoice,
#         amount,
#         payment_date,
#         payment_method,
#         reference="",
#         remarks="",
#     ):
#         """
#         Record a payment and automatically
#         update the invoice status.
#         """

#         amount = Decimal(amount)

#         if amount <= Decimal("0.00"):
#             raise ValueError(
#                 "Payment amount must be greater than zero."
#             )

#         balance = FeeService.get_balance(invoice)

#         if amount > balance:
#             raise ValueError(
#                 "Payment cannot be greater than "
#                 "the outstanding balance."
#             )

#         payment = Payment.objects.create(
#             invoice=invoice,
#             amount=amount,
#             payment_date=payment_date,
#             payment_method=payment_method,
#             reference=reference,
#             remarks=remarks,
#         )

#         FeeService.update_invoice_status(
#             invoice
#         )

#         return payment


#     @staticmethod
#     def get_invoice_summary(invoice):

#         paid = FeeService.get_paid_amount(
#             invoice
#         )

#         balance = FeeService.get_balance(
#             invoice
#         )

#         return {
#             "invoice": invoice,
#             "amount": invoice.amount,
#             "paid": paid,
#             "balance": balance,
#             "status": invoice.status,
#         }

#     @staticmethod
#     def get_payment_history(invoice):
#         return invoice.payments.all().order_by(
#             "-payment_date",
#             "-id",
#         )

#     @staticmethod
#     def get_student_fee_summary(student):
#         invoices = FeeInvoice.objects.filter(
#             enrollment__student=student
#         )

#         total_invoiced = (
#             invoices.aggregate(
#                 total=Sum("amount")
#             )["total"]
#             or Decimal("0.00")
#         )

#         total_paid = (
#             Payment.objects.filter(
#                 invoice__enrollment__student=student
#             ).aggregate(
#                 total=Sum("amount")
#             )["total"]
#             or Decimal("0.00")
#         )

#         outstanding = total_invoiced - total_paid

#         return {
#             "total_invoiced": total_invoiced,
#             "total_paid": total_paid,
#             "outstanding": outstanding,
#         }