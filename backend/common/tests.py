"""
Tests for row scoping.

visible_employees() decides which employee rows a person may see. Every
list endpoint, the dashboard, and all ten AI tools filter through it — so
if it is wrong, it is wrong everywhere at once.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from common.scoping import visible_employees
from employees.models import Employee
from organizations.models import Department, Designation

User = get_user_model()


class ScopingTests(TestCase):
    """A manager, their report, and someone from another team."""

    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="Engineering", code="ENG")
        cls.designation = Designation.objects.create(title="Engineer")

        cls.admin_user = cls._user("admin@test.com", User.Roles.ADMIN)
        cls.hr_user = cls._user("hr@test.com", User.Roles.HR)
        cls.manager_user = cls._user("manager@test.com", User.Roles.MANAGER)
        cls.report_user = cls._user("report@test.com", User.Roles.EMPLOYEE)
        cls.outsider_user = cls._user("outsider@test.com", User.Roles.EMPLOYEE)

        cls.manager = cls._employee(cls.manager_user, "ENG001", manager=None)
        cls.report = cls._employee(cls.report_user, "ENG002", manager=cls.manager)
        cls.outsider = cls._employee(cls.outsider_user, "ENG003", manager=None)

    @classmethod
    def _user(cls, email, role):
        return User.objects.create_user(
            email=email, password="Password@123", role=role, is_verified=True
        )

    @classmethod
    def _employee(cls, user, employee_id, manager):
        return Employee.objects.create(
            user=user,
            employee_id=employee_id,
            department=cls.department,
            designation=cls.designation,
            manager=manager,
            date_of_joining=date(2024, 1, 1),
        )

    # -- who sees everyone ---------------------------------------------------

    def test_admin_sees_everyone(self):
        visible = visible_employees(self.admin_user)
        self.assertEqual(visible.count(), 3)

    def test_hr_sees_everyone(self):
        visible = visible_employees(self.hr_user)
        self.assertEqual(visible.count(), 3)

    # -- who sees a subset ---------------------------------------------------

    def test_manager_sees_themselves_and_their_report(self):
        visible = set(visible_employees(self.manager_user))
        self.assertEqual(visible, {self.manager, self.report})

    def test_manager_cannot_see_another_team(self):
        visible = visible_employees(self.manager_user)
        self.assertNotIn(self.outsider, visible)

    def test_employee_sees_only_themselves(self):
        visible = set(visible_employees(self.report_user))
        self.assertEqual(visible, {self.report})

    def test_employee_cannot_see_their_own_manager(self):
        # Reporting upwards is not visibility. A report has no business
        # reading their manager's record.
        visible = visible_employees(self.report_user)
        self.assertNotIn(self.manager, visible)

    # -- edge case -----------------------------------------------------------

    def test_a_user_with_no_employee_record_sees_nobody(self):
        # HR and Admin accounts often have no Employee row. For anyone else
        # this must come back empty, not blow up and not return everything.
        orphan = self._user("orphan@test.com", User.Roles.EMPLOYEE)
        self.assertEqual(visible_employees(orphan).count(), 0)
