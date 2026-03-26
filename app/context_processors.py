from .models import Membership


def organization_context(request):
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {}

    active_org = getattr(request, "active_organization", None)
    memberships = Membership.objects.filter(user=request.user).select_related(
        "organization"
    )
    user_organizations = [m.organization for m in memberships]

    # Check if current user is admin of the active org
    is_org_admin = False
    if active_org:
        is_org_admin = memberships.filter(
            organization=active_org, role="admin"
        ).exists()

    return {
        "active_organization": active_org,
        "user_organizations": user_organizations,
        "is_org_admin": is_org_admin,
    }
