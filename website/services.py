from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import ContactMessage, SchoolEvent


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

    @classmethod
    def get_popup_event(cls):

        today = timezone.localdate()

        return (
            SchoolEvent.objects
            .filter(
                is_active=True,
                show_popup=True,
                event_date__gte=today,
            )
            .order_by(
                "event_date",
                "event_time",
            )
            .first()
        )


    @classmethod
    def get_upcoming_events(cls, limit=3):

        today = timezone.localdate()

        return (
            SchoolEvent.objects
            .filter(
                is_active=True,
                event_date__gte=today,
            )
            .order_by(
                "event_date",
                "event_time",
            )[:limit]
        )

    
    @classmethod
    def get_public_events(cls):
        today = timezone.localdate()

        upcoming_events = (
            SchoolEvent.objects
            .filter(
                is_active=True,
                event_date__gte=today,
            )
            .order_by(
                "event_date",
                "event_time",
            )
        )

        past_events = (
            SchoolEvent.objects
            .filter(
                is_active=True,
                event_date__lt=today,
            )
            .order_by(
                "-event_date",
                "-event_time",
            )
        )

        return {
            "upcoming": upcoming_events,
            "past": past_events,
        }


    @classmethod
    def get_public_event_detail(cls, slug):

        return (
            SchoolEvent.objects
            .filter(
                slug=slug,
                is_active=True,
            )
            .first()
        )

