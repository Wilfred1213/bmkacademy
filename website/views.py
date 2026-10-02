from .forms import ContactMessageForm
from .services import WebsiteService

from gallery.services import GalleryService

from blog.services import BlogService

from django.http import Http404
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from academics.services import AcademicService
from academics.models import SchoolClass



def home(request):

    hero_slides = WebsiteService.get_active_hero_slides()

    latest_posts = BlogService.get_latest_posts(
        limit=3
    )

    featured_photos = GalleryService.get_featured_photos(
        limit=4
    )

    popup_event = WebsiteService.get_popup_event()

    upcoming_events = WebsiteService.get_upcoming_events(
        limit=3
    )

    return render(
        request,
        "website/home.html",
        {
            "hero_slides": hero_slides,
            "latest_posts": latest_posts,
            "featured_photos": featured_photos,
            "popup_event": popup_event,
            "upcoming_events": upcoming_events,
        },
    )




def safeguarding(request):
    return render(
        request,
        "website/safeguarding.html",
    )

def about(request):
    return render(
        request,
        "website/about.html",
    )

def academics(request):
    academic_sections = AcademicService.get_public_academic_sections()

    return render(
        request,
        "website/academics.html",
        {
            "academic_sections": academic_sections,
        },
    )
def contact(request):

    if request.method == "POST":

        form = ContactMessageForm(request.POST)

        if form.is_valid():

            WebsiteService.submit_contact_message(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data["phone"],
                subject=form.cleaned_data["subject"],
                message=form.cleaned_data["message"],
            )

            messages.success(
                request,
                "Thank you for contacting BMK Academy. "
                "Your message has been received."
            )

            return redirect("website:contact")

    else:
        form = ContactMessageForm()

    return render(
        request,
        "website/contact.html",
        {
            "form": form,
        },
    )

def academic_class_detail(request, slug):
    try:
        school_class = AcademicService.get_public_class_detail(slug)
    except SchoolClass.DoesNotExist:
        raise Http404

    return render(
        request,
        "website/academic_class_detail.html",
        {
            "school_class": school_class,
        },
    )


def events(request):

    public_events = WebsiteService.get_public_events()

    return render(
        request,
        "website/events.html",
        {
            "upcoming_events": public_events["upcoming"],
            "past_events": public_events["past"],
        },
    )

def event_detail(request, slug):

    event = WebsiteService.get_public_event_detail(
        slug
    )

    if not event:
        raise Http404

    return render(
        request,
        "website/event_detail.html",
        {
            "event": event,
        },
    )

