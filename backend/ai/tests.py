"""
Tests for the AI tools.

Every tool takes the authenticated user as its first argument and filters
through visible_employees(). These tests prove that holds — a tool must
never return a row the person asking could not reach through the normal API.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from ai.tools import TOOL_SCHEMAS, TOOLS, WRITE_TOOLS, run_tool
from employees.models import Employee
from organizations.models import Department, Designation

User = get_user_model()


class ToolScopingTests(TestCase):
    """A manager, their report, and someone from another team."""

    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="Engineering", code="ENG")
        cls.designation = Designation.objects.create(title="Engineer")

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

    @staticmethod
    def _ids(result):
        """The employee IDs a tool returned."""
        return {row["employee_id"] for row in result["employees"]}

    # -- search_employees ----------------------------------------------------

    def test_hr_search_returns_everyone(self):
        result = TOOLS["search_employees"](self.hr_user)
        self.assertEqual(self._ids(result), {"ENG001", "ENG002", "ENG003"})

    def test_manager_search_returns_only_their_team(self):
        result = TOOLS["search_employees"](self.manager_user)
        self.assertEqual(self._ids(result), {"ENG001", "ENG002"})

    def test_employee_search_returns_only_themselves(self):
        result = TOOLS["search_employees"](self.report_user)
        self.assertEqual(self._ids(result), {"ENG002"})

    def test_searching_by_name_cannot_reach_outside_scope(self):
        # Naming someone explicitly must not widen what you can see.
        result = TOOLS["search_employees"](self.report_user, query="outsider")
        self.assertEqual(result["employees"], [])

    # -- get_employee_details ------------------------------------------------

    def test_details_of_an_out_of_scope_employee_are_refused(self):
        result = TOOLS["get_employee_details"](self.report_user, "ENG003")
        self.assertIn("error", result)

    def test_details_of_an_in_scope_employee_are_returned(self):
        result = TOOLS["get_employee_details"](self.manager_user, "ENG002")
        self.assertNotIn("error", result)

    # -- get_leave_balance ---------------------------------------------------

    def test_balance_of_an_out_of_scope_employee_is_refused(self):
        result = TOOLS["get_leave_balance"](self.report_user, employee_id="ENG003")
        self.assertIn("error", result)


class RunToolTests(TestCase):
    """run_tool is the only entry point the agent loop uses."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="someone@test.com",
            password="Password@123",
            role=User.Roles.EMPLOYEE,
            is_verified=True,
        )

    def test_an_unknown_tool_returns_an_error_rather_than_raising(self):
        # The model invents tool names. A crash here would end the
        # conversation; an error lets it try something else.
        result = run_tool("delete_everything", {}, self.user)
        self.assertIn("error", result)

    def test_bad_arguments_return_an_error_rather_than_raising(self):
        result = run_tool("search_employees", {"nonsense": 1}, self.user)
        self.assertIn("error", result)

    def test_every_schema_has_a_function_behind_it(self):
        # A schema with no function means the model can ask for something
        # that does not exist. Easy to introduce, invisible until it happens.
        for schema in TOOL_SCHEMAS:
            self.assertIn(schema["name"], TOOLS)

    def test_every_write_tool_is_a_real_tool(self):
        for name in WRITE_TOOLS:
            self.assertIn(name, TOOLS)
