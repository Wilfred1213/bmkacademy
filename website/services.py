from django.conf import settings
from django.core.mail import send_mail

from .models import ContactMessage


class WebsiteService:

    @classmethod
    def get_active_hero_slides(cls):
        from .models import HeroSlide

        return (
            HeroSlide.objects
            .filter(is_active=True)
            .order_by("order", "-created_at")
        )

    @classmethod
    def submit_contact_message(
        cls,
        name,
        email,
        phone,
        subject,
        message,
    ):
        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
        )

        send_mail(
            subject=f"BMK Website Enquiry: {subject}",
            message=(
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone or 'Not provided'}\n\n"
                f"Message:\n"
                f"{message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        return contact_message