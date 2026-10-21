from rest_framework.permissions import BasePermission

from apps.organizations.models import Membership


class ProductPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        org_id = request.headers.get("X-Organization-ID")

        if not org_id:
            return False

        membership = Membership.objects.filter(
            organization_id=org_id,
            user=request.user,
        ).first()

        if not membership:
            return False

        if view.action in ["list", "retrieve"]:
            return True

        return membership.role in [
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
            Membership.Role.STAFF,
        ]