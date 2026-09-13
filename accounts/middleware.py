from django.shortcuts import redirect
from django.urls import reverse


class PasswordChangeRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated and request.user.must_change_password:

            allowed_urls = {
                reverse("accounts:change_password"),
                reverse("accounts:logout"),
            }

            if request.path not in allowed_urls:
                return redirect("accounts:change_password")

        return self.get_response(request)