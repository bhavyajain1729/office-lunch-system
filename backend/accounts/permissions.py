"""
Reusable DRF permission classes based on the User.role field.
"""

from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allows access only to users with role == ADMIN."""

    message = "Only admin accounts can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "ADMIN"
        )


class IsEmployeeRole(BasePermission):
    """Allows access only to users with role == EMPLOYEE."""

    message = "Only employee accounts can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "EMPLOYEE"
        )
