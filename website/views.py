from .forms import ContactMessageForm
from .services import WebsiteService

from gallery.services import GalleryService

from blog.services import BlogService

from django.http import Http404
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from academics.services import AcademicService
from .forms import ContactMessageForm


def home(request):
    hero_slides = WebsiteService.get_active_hero_slides()
    latest_posts = BlogService.get_latest_posts(limit=3)
    featured_photos = GalleryService.get_featured_photos(limit=4)

    return render(
        request,
        "website/home.html",
        {
            "hero_slides": hero_slides,
            "latest_posts": latest_posts,
            "featured_photos": featured_photos,
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