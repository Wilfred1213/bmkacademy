from django.urls import path
from . import views


app_name = "website"


urlpatterns = [

    path(
        "",
        views.home,
        name="home",
    ),
    path("academics/", views.academics, name="academics"),
    path("about/", views.about, name="about"),
    path("safeguarding/", views.safeguarding, name="safeguarding"),
    path("contact/", views.contact, name="contact"),
    path(
    "academics/class/<slug:slug>/",
    views.academic_class_detail,
    name="academic_class_detail",
    ),
    # id="x2kh6h"
    path(
        "events/",
        views.events,
        name="events",
    ),

    path(
        "events/<slug:slug>/",
        views.event_detail,
        name="event_detail",
    ),

]
