"""
Row-level scoping, in one place.

Three viewsets and the dashboard all need the same answer to "which
employees may this user see". Defining it once means they cannot drift.
"""

from django.db.models import Q


def visible_employee_filter(user):
    """
    A Q object for Employee rows, or None meaning "no filter — see everything".

    Admin and HR see everyone. Everyone else sees themselves plus anyone who
    reports to them. Deliberately read off the org chart rather than
    User.role, because the role flag drifts out of sync with Employee.manager.
    """
    Roles = user.Roles
    if user.role in (Roles.ADMIN, Roles.HR):
        return None
    return Q(user=user) | Q(manager__user=user)


def visible_employees(user):
    """The Employee queryset this user may see."""
    from employees.models import Employee

    scope = visible_employee_filter(user)
    queryset = Employee.objects.all()
    return queryset if scope is None else queryset.filter(scope)
