import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone


logger = logging.getLogger(__name__)


class NotificationEmailService:

    
    @staticmethod
    def send_admission_decision_email(
        application,
        decision,
    ):
        """
        Send an admission decision email to the applicant.

        For approved applications, the email includes the
        parent-account claim link.

        Returns:
            True  -> email sent successfully
            False -> email failed
        """

        # ---------------------------------------------------------
        # 1. Make sure we have an email address
        # ---------------------------------------------------------

        if not application.parent_email:
            logger.warning(
                "No email address for admission application %s",
                application.id,
            )
            return False

        # ---------------------------------------------------------
        # 2. Count this email attempt
        # ---------------------------------------------------------

        application.admission_email_attempts += 1

        application.save(
            update_fields=[
                "admission_email_attempts"
            ]
        )

        # ---------------------------------------------------------
        # 3. Build the email
        # ---------------------------------------------------------

        if decision == "approved":

            # Make sure an approved application has a claim token
            if not application.claim_token:
                logger.error(
                    "Approved application %s has no claim token.",
                    application.id,
                )

                application.admission_email_last_error = (
                    "Approved application has no claim token."
                )

                application.save(
                    update_fields=[
                        "admission_email_last_error"
                    ]
                )

                return False

            claim_path = reverse(
                "admissions:claim_application",
                kwargs={
                    "claim_token": application.claim_token
                },
            )

            claim_url = (
                f"{settings.SITE_URL}"
                f"{claim_path}"
            )

            subject = "BMK Academy - Admission Approved"

            message = (
                f"Dear {application.parent_name},\n\n"

                f"Congratulations!\n\n"

                f"The admission application for "
                f"{application.first_name} "
                f"{application.middle_name} "
                f"{application.last_name} "
                f"has been approved.\n\n"

                f"Class: {application.desired_class}\n"
                f"Academic Year: {application.academic_year}\n"
                f"Term: {application.term}\n\n"

                f"To access the BMK Academy Parent Portal, "
                f"please create your parent account using "
                f"the secure link below:\n\n"

                f"{claim_url}\n\n"

                f"This account-creation link will expire "
                f"in 48 hours.\n\n"

                f"Once your account has been created, you will "
                f"be able to log in to the BMK Academy Parent "
                f"Portal and access information about your child.\n\n"

                f"Thank you for choosing BMK Academy.\n\n"

                f"Regards,\n"
                f"BMK Academy"
            )

        elif decision == "rejected":

            subject = "BMK Academy - Admission Application Update"

            message = (
                f"Dear {application.parent_name},\n\n"

                f"We regret to inform you that the admission "
                f"application for "
                f"{application.first_name} "
                f"{application.middle_name} "
                f"{application.last_name} "
                f"has been rejected.\n\n"

                f"Academic Year: {application.academic_year}\n"
                f"Term: {application.term}\n\n"

                f"If you require further information, "
                f"please contact BMK Academy.\n\n"

                f"Regards,\n"
                f"BMK Academy"
            )

        else:

            raise ValueError(
                "Decision must be 'approved' or 'rejected'."
            )

        # ---------------------------------------------------------
        # 4. Send the email
        # ---------------------------------------------------------

        try:

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    application.parent_email
                ],
                fail_silently=False,
            )

        except Exception as exc:

            # -----------------------------------------------------
            # 5. Record the failure
            # -----------------------------------------------------

            application.admission_email_last_error = str(exc)

            application.save(
                update_fields=[
                    "admission_email_last_error"
                ]
            )

            logger.exception(
                "Failed to send admission email for "
                "application %s",
                application.id,
            )

            return False

        # ---------------------------------------------------------
        # 6. Record successful delivery to SMTP
        # ---------------------------------------------------------

        application.admission_email_sent = True

        application.admission_email_sent_at = timezone.now()

        application.admission_email_last_error = ""

        application.save(
            update_fields=[
                "admission_email_sent",
                "admission_email_sent_at",
                "admission_email_last_error",
            ]
        )

        logger.info(
            "Admission email sent successfully for "
            "application %s",
            application.id,
        )

        return True

    @staticmethod
    def send_announcement_email(
        recipient,
        title,
        message,
    ):
        """
        Send a school announcement email to one user.

        Returns:
            True  -> email sent successfully
            False -> email failed
        """

        if not recipient.email:
            logger.warning(
                "No email address for user %s",
                recipient.username,
            )
            return False

        try:

            send_mail(
                subject=f"BMK Academy - {title}",
                message=(
                    f"Dear {recipient.first_name or 'Parent'},\n\n"
                    f"{message}\n\n"
                    f"Please log in to the BMK Academy Parent Portal "
                    f"for more information.\n\n"
                    f"Regards,\n"
                    f"BMK Academy"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    recipient.email
                ],
                fail_silently=False,
            )

        except Exception as exc:

            logger.exception(
                "Failed to send announcement email "
                "to user %s",
                recipient.username,
            )

            return False

        logger.info(
            "Announcement email sent successfully "
            "to user %s",
            recipient.username,
        )

        return True