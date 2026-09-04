"""
Tests for the human-in-the-loop gate.

The claim being tested: the agent can propose a write but never perform one,
and a proposal can be acted on exactly once, by someone allowed to act on it.

Nothing here calls the model. The gate lives in the loop and in decide(),
so it can be tested without spending a single API call.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import TestCase
from django.utils import timezone

from ai.models import Conversation, PendingAction
from ai.services import _propose, decide
from employees.models import Employee
from leave.models import LeaveBalance, LeaveRequest, LeaveType
from organizations.models import Department, Designation

User = get_user_model()


class ApprovalGateTests(TestCase):
    def setUp(self):
        # setUp, not setUpTestData: these tests change the rows they use, so
        # each one needs its own copy.
        self.department = Department.objects.create(name="Engineering", code="ENG")
        self.designation = Designation.objects.create(title="Engineer")
        self.annual = LeaveType.objects.create(
            name="Annual Leave", code="ANNUAL", default_days_per_year=30
        )

        self.manager_user = self._user("manager@test.com", User.Roles.MANAGER)
        self.report_user = self._user("report@test.com", User.Roles.EMPLOYEE)
        self.outsider_user = self._user("outsider@test.com", User.Roles.EMPLOYEE)

        self.manager = self._employee(self.manager_user, "ENG001", manager=None)
        self.report = self._employee(self.report_user, "ENG002", manager=self.manager)
        self.outsider = self._employee(self.outsider_user, "ENG003", manager=None)

        start = timezone.localdate() + timedelta(days=30)
        while start.weekday() >= 5:
            start += timedelta(days=1)

        self.balance = LeaveBalance.objects.create(
            employee=self.report,
            leave_type=self.annual,
            year=start.year,
            allocated=Decimal("30"),
            pending=Decimal("3"),
        )
        self.request = LeaveRequest.objects.create(
            employee=self.report,
            leave_type=self.annual,
            start_date=start,
            end_date=start + timedelta(days=2),
            days=Decimal("3"),
        )

        self.conversation = Conversation.objects.create(user=self.manager_user)

    def _user(self, email, role):
        return User.objects.create_user(
            email=email, password="Password@123", role=role, is_verified=True
        )

    def _employee(self, user, employee_id, manager):
        return Employee.objects.create(
            user=user,
            employee_id=employee_id,
            department=self.department,
            designation=self.designation,
            manager=manager,
            date_of_joining=date(2024, 1, 1),
        )

    def _propose_approval(self, user=None):
        return _propose(
            self.conversation,
            user or self.manager_user,
            "approve_leave_request",
            {"request_id": str(self.request.id)},
        )

    # -- proposing changes nothing -------------------------------------------

    def test_proposing_creates_a_pending_action(self):
        output = self._propose_approval()
        self.assertEqual(output["status"], "awaiting_approval")
        self.assertEqual(PendingAction.objects.count(), 1)

    def test_proposing_does_not_touch_the_leave_request(self):
        # The whole point. This is the assertion the elif bug would fail.
        self._propose_approval()
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, LeaveRequest.Status.PENDING)

    def test_proposing_does_not_move_the_balance(self):
        self._propose_approval()
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.used, Decimal("0"))
        self.assertEqual(self.balance.pending, Decimal("3"))

    def test_someone_who_cannot_approve_gets_no_proposal(self):
        output = self._propose_approval(user=self.outsider_user)
        self.assertIn("error", output)
        self.assertEqual(PendingAction.objects.count(), 0)

    # -- approving does the work ---------------------------------------------

    def test_approving_changes_the_leave_request(self):
        action_id = self._propose_approval()["action_id"]
        decide(action_id=action_id, user=self.manager_user, approve=True)

        self.request.refresh_from_db()
        self.assertEqual(self.request.status, LeaveRequest.Status.APPROVED)

    def test_approving_moves_pending_into_used(self):
        action_id = self._propose_approval()["action_id"]
        decide(action_id=action_id, user=self.manager_user, approve=True)

        self.balance.refresh_from_db()
        self.assertEqual(self.balance.used, Decimal("3"))
        self.assertEqual(self.balance.pending, Decimal("0"))

    def test_rejecting_leaves_the_request_pending(self):
        action_id = self._propose_approval()["action_id"]
        decide(action_id=action_id, user=self.manager_user, approve=False)

        self.request.refresh_from_db()
        self.assertEqual(self.request.status, LeaveRequest.Status.PENDING)

    # -- decided once, and only once -----------------------------------------

    def test_the_same_action_cannot_be_approved_twice(self):
        action_id = self._propose_approval()["action_id"]
        decide(action_id=action_id, user=self.manager_user, approve=True)

        with self.assertRaises(ValidationError):
            decide(action_id=action_id, user=self.manager_user, approve=True)

    def test_an_expired_action_cannot_be_approved(self):
        action_id = self._propose_approval()["action_id"]
        PendingAction.objects.filter(pk=action_id).update(
            expires_at=timezone.now() - timedelta(minutes=1)
        )

        with self.assertRaises(ValidationError):
            decide(action_id=action_id, user=self.manager_user, approve=True)

        self.request.refresh_from_db()
        self.assertEqual(self.request.status, LeaveRequest.Status.PENDING)

    def test_another_users_action_cannot_be_approved(self):
        # decide() is scoped to the caller's own conversation. Not-yours and
        # not-found are the same 404 on purpose.
        action_id = self._propose_approval()["action_id"]

        with self.assertRaises(Http404):
            decide(action_id=action_id, user=self.outsider_user, approve=True)
