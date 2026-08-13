from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()
Roles = User.Roles


class RolePermission(permissions.BasePermission):
    """
    Base permission for role-based access.
    Child classes set `allowed_roles`.

    Admin is a super role: it passes every check. That rule lives here so a
    new permission class can never forget to include it.
    """

    allowed_roles = ()

    def has_permission(self, request, view):
        user = request.user

        if not (user and user.is_authenticated):
            return False

        if user.role == Roles.ADMIN:
            return True

        return user.role in self.allowed_roles


class IsAdmin(RolePermission):
    """Accounts and system settings."""

    allowed_roles = (Roles.ADMIN,)


class IsHR(RolePermission):
    """Employees, leave, documents."""

    allowed_roles = (Roles.HR, Roles.ADMIN,)


class IsManager(RolePermission):
    """Approving and viewing their own team."""

    allowed_roles = (Roles.MANAGER,)


class IsEmployee(RolePermission):
    """Self-service only."""

    allowed_roles = (Roles.EMPLOYEE,)


class IsSelfOrHR(permissions.BasePermission):
    """
    Object-level: you can touch your own record. HR and Admin can touch any.

    Only runs on detail routes — list views never call get_object(), so they
    are secured by filtering get_queryset() instead.
    """

    def has_permission(self, request, view):
        # Without this, an anonymous request reaches has_object_permission
        # and crashes on AnonymousUser.role.
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role in (Roles.ADMIN, Roles.HR):
            return True

        # The object is either the user itself (/me) or something pointing at
        # a user (Employee.user). Handle both.
        if obj == user:
            return True

        # user_id instead of user avoids loading the related row.
        return getattr(obj, "user_id", None) == user.id


class ReadOnly(permissions.BasePermission):
    """
    Allows GET / HEAD / OPTIONS only.

    Meant to be combined: `permission_classes = [IsHR | ReadOnly]` reads as
    "HR can change it, everyone else can only look".
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
