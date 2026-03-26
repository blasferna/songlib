from django.shortcuts import redirect
from django.urls import resolve, reverse

from .models import Membership, UserProfile

# URL names that don't require an active organization
EXEMPT_URL_NAMES = {
    "login",
    "logout",
    "register",
    "organization_list",
    "organization_create",
    "organization_switch",
    "setlist_detail",
    "setlist_export_txt",
    "setlist_reader",
}

EXEMPT_URL_PREFIXES = ("/admin/", "/api/")


class ActiveOrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.active_organization = None

        if request.user.is_authenticated:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            request.active_organization = profile.active_organization

            # Auto-select if user has exactly one organization
            if not request.active_organization:
                memberships = Membership.objects.filter(
                    user=request.user
                ).select_related("organization")
                if memberships.count() == 1:
                    profile.active_organization = memberships.first().organization
                    profile.save(update_fields=["active_organization"])
                    request.active_organization = profile.active_organization
                else:
                    path = request.path
                    resolved = resolve(path)
                    url_name = resolved.url_name

                    is_exempt = (
                        url_name in EXEMPT_URL_NAMES
                        or any(path.startswith(p) for p in EXEMPT_URL_PREFIXES)
                    )

                    if not is_exempt:
                        return redirect("organization_list")

        return self.get_response(request)
