"""
Tests for the leave service.

The balance arithmetic is the easiest thing in this project to get subtly
wrong, and the failure is silent: nothing errors, the numbers just drift.
So the invariant

    allocated = used + pending + available

is asserted after every path out of PENDING.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from employees.models import Employee
from organizations.models import Department, Designation

from .models import LeaveBalance, LeaveRequest, LeaveType
from .services import (
    apply_leave,
    approve_leave,
    can_approve,
    cancel_leave,
    get_balance,
    reject_leave,
    working_days,
)

User = get_user_model()


def next_monday(weeks_ahead=4):
    """A Monday comfortably in the future, so past-date checks never fire."""
    today = timezone.localdate()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    return today + timedelta(days=days_until_monday + 7 * weeks_ahead)


class WorkingDaysTests(TestCase):
    """Pure function, fixed dates. 2026-08-14 is a Friday."""

    def test_weekend_in_the_middle_is_skipped(self):
        # Fri 14 -> Mon 17 August. Saturday and Sunday do not count.
        self.assertEqual(working_days(date(2026, 8, 14), date(2026, 8, 17)), Decimal(2))

    def test_single_day_counts_as_one(self):
        # Not zero. The naive (end - start).days answer is off by one.
        self.assertEqual(working_days(date(2026, 8, 17), date(2026, 8, 17)), Decimal(1))

    def test_full_week(self):
        self.assertEqual(working_days(date(2026, 8, 17), date(2026, 8, 21)), Decimal(5))

    def test_weekend_only_is_zero(self):
        self.assertEqual(working_days(date(2026, 8, 15), date(2026, 8, 16)), Decimal(0))

    def test_end_before_start_is_rejected(self):
        with self.assertRaises(ValidationError):
            working_days(date(2026, 8, 20), date(2026, 8, 10))


class LeaveTestCase(TestCase):
    """Shared fixture: a manager, a direct report, an outsider, and HR."""

    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="Engineering", code="ENG")
        cls.designation = Designation.objects.create(title="Engineer")

        cls.annual = LeaveType.objects.create(
            name="Annual Leave", code="ANNUAL", default_days_per_year=30
        )
        cls.unpaid = LeaveType.objects.create(
            name="Unpaid Leave", code="UNPAID", default_days_per_year=0, is_active=False
        )

        cls.hr_user = cls._user("hr@test.com", User.Roles.HR)
        cls.manager_user = cls._user("manager@test.com", User.Roles.MANAGER)
        cls.report_user = cls._user("report@test.com", User.Roles.EMPLOYEE)
        cls.outsider_user = cls._user("outsider@test.com", User.Roles.EMPLOYEE)

        cls.manager = cls._employee(cls.manager_user, manager=None)
        cls.report = cls._employee(cls.report_user, manager=cls.manager)
        cls.outsider = cls._employee(cls.outsider_user, manager=None)

        cls.year = next_monday().year
        for employee in (cls.manager, cls.report, cls.outsider):
            LeaveBalance.objects.create(
                employee=employee,
                leave_type=cls.annual,
                year=cls.year,
                allocated=Decimal("30"),
            )

    @classmethod
    def _user(cls, email, role):
        return User.objects.create_user(
            email=email, password="Password@123", role=role, is_verified=True
        )

    @classmethod
    def _employee(cls, user, manager):
        return Employee.objects.create(
            user=user,
            employee_id=f"ENG{user.email[:4].upper()}",
            department=cls.department,
            designation=cls.designation,
            manager=manager,
            date_of_joining=date(2024, 1, 1),
        )

    def assert_invariant(self, employee, leave_type=None):
        balance = get_balance(employee, leave_type or self.annual, self.year)
        self.assertEqual(
            balance.allocated,
            balance.used + balance.pending + balance.available,
            "allocated must equal used + pending + available",
        )
        self.assertGreaterEqual(balance.used, 0)
        self.assertGreaterEqual(balance.pending, 0)
        return balance


class ApplyLeaveTests(LeaveTestCase):
    def test_applying_places_a_hold_not_a_deduction(self):
        start = next_monday()
        request = apply_leave(
            employee=self.report,
            leave_type=self.annual,
            start_date=start,
            end_date=start + timedelta(days=4),
        )

        self.assertEqual(request.status, LeaveRequest.Status.PENDING)
        self.assertEqual(request.days, Decimal(5))

        balance = self.assert_invariant(self.report)
        self.assertEqual(balance.pending, Decimal(5))
        self.assertEqual(balance.used, Decimal(0))
        self.assertEqual(balance.available, Decimal(25))

    def test_days_exclude_weekends(self):
        friday = next_monday() + timedelta(days=4)
        request = apply_leave(
            employee=self.report,
            leave_type=self.annual,
            start_date=friday,
            end_date=friday + timedelta(days=3),  # Fri -> Mon
        )
        self.assertEqual(request.days, Decimal(2))

    def test_past_dates_are_rejected(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            apply_leave(
                employee=self.report,
                leave_type=self.annual,
                start_date=yesterday,
                end_date=yesterday,
            )

    def test_weekend_only_range_is_rejected(self):
        saturday = next_monday() + timedelta(days=5)
        with self.assertRaises(ValidationError):
            apply_leave(
                employee=self.report,
                leave_type=self.annual,
                start_date=saturday,
                end_date=saturday + timedelta(days=1),
            )

    def test_inactive_leave_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            apply_leave(
                employee=self.report,
                leave_type=self.unpaid,
                start_date=next_monday(),
                end_date=next_monday(),
            )

    def test_more_days_than_available_is_rejected(self):
        start = next_monday()
        with self.assertRaises(ValidationError):
            apply_leave(
                employee=self.report,
                leave_type=self.annual,
                start_date=start,
                end_date=start + timedelta(days=90),
            )
        self.assertEqual(self.assert_invariant(self.report).pending, Decimal(0))

    def test_missing_balance_is_rejected(self):
        LeaveBalance.objects.filter(employee=self.report).delete()
        with self.assertRaises(ValidationError):
            apply_leave(
                employee=self.report,
                leave_type=self.annual,
                start_date=next_monday(),
                end_date=next_monday(),
            )

    def test_two_pending_requests_cannot_exceed_the_balance(self):
        """The reason `pending` exists as a separate column."""
        first = next_monday()
        apply_leave(
            employee=self.report,
            leave_type=self.annual,
            start_date=first,
            end_date=first + timedelta(days=25),  # 20 working days
        )
        second = next_monday(weeks_ahead=12)
        with self.assertRaises(ValidationError):
            apply_leave(
                employee=self.report,
                leave_type=self.annual,
                start_date=second,
                end_date=second + timedelta(days=25),
            )


class OverlapTests(LeaveTestCase):
    def setUp(self):
        self.start = next_monday()
        self.end = self.start + timedelta(days=4)
        self.existing = apply_leave(
            employee=self.report,
            leave_type=self.annual,
            start_date=self.start,
            end_date=self.end,
        )

    def _expect_clash(self, start, end):
        with self.assertRaises(ValidationError):
            apply_leave(
                employee=self.report,
                leave_type=self.annual,
                start_date=start,
                end_date=end,
            )

    def test_identical_range(self):
        self._expect_clash(self.start, self.end)

    def test_range_inside_the_existing_one(self):
        self._expect_clash(self.start + timedelta(days=1), self.end - timedelta(days=1))

    def test_range_that_swallows_the_existing_one(self):
        """The case a naive 'is the start inside?' check misses."""
        self._expect_clash(self.start - timedelta(days=3), self.end + timedelta(days=3))

    def test_range_overlapping_only_the_start(self):
        self._expect_clash(self.start - timedelta(days=2), self.start)

    def test_adjacent_range_does_not_clash(self):
        later = self.end + timedelta(days=3)
        request = apply_leave(
            employee=self.report,
            leave_type=self.annual,
            start_date=later,
            end_date=later,
        )
        self.assertEqual(request.status, LeaveRequest.Status.PENDING)

    def test_a_rejected_request_stops_blocking_the_dates(self):
        reject_leave(leave_request=self.existing, approver=self.hr_user)
        request = apply_leave(
            employee=self.report,
            leave_type=self.annual,
            start_date=self.start,
            end_date=self.end,
        )
        self.assertEqual(request.status, LeaveRequest.Status.PENDING)

    def test_another_employee_is_unaffected(self):
        request = apply_leave(
            employee=self.outsider,
            leave_type=self.annual,
            start_date=self.start,
            end_date=self.end,
        )
        self.assertEqual(request.status, LeaveRequest.Status.PENDING)


class CanApproveTests(LeaveTestCase):
    def setUp(self):
        start = next_monday()
        self.report_request = apply_leave(
            employee=self.report,
            leave_type=self.annual,
            start_date=start,
            end_date=start + timedelta(days=2),
        )
        self.manager_request = apply_leave(
            employee=self.manager,
            leave_type=self.annual,
            start_date=start,
            end_date=start + timedelta(days=2),
        )

    def test_manager_may_approve_their_direct_report(self):
        self.assertTrue(can_approve(self.manager_user, self.report_request))

    def test_manager_may_not_approve_their_own_request(self):
        self.assertFalse(can_approve(self.manager_user, self.manager_request))

    def test_manager_may_not_approve_outside_their_team(self):
        start = next_monday(weeks_ahead=8)
        outsider_request = apply_leave(
            employee=self.outsider,
            leave_type=self.annual,
            start_date=start,
            end_date=start,
        )
        self.assertFalse(can_approve(self.manager_user, outsider_request))

    def test_hr_may_approve_anyone(self):
        self.assertTrue(can_approve(self.hr_user, self.report_request))
        self.assertTrue(can_approve(self.hr_user, self.manager_request))

    def test_admin_may_not_approve_their_own_request(self):
        """The self-check runs before the role check, so it beats the super-role."""
        self.manager_user.role = User.Roles.ADMIN
        self.assertFalse(can_approve(self.manager_user, self.manager_request))

    def test_an_employee_may_not_approve_their_own_request(self):
        self.assertFalse(can_approve(self.report_user, self.report_request))


class DecisionTests(LeaveTestCase):
    def setUp(self):
        self.start = next_monday()
        self.request = apply_leave(
            employee=self.report,
            leave_type=self.annual,
            start_date=self.start,
            end_date=self.start + timedelta(days=4),
        )

    def test_approving_moves_pending_into_used(self):
        approve_leave(leave_request=self.request, approver=self.manager_user)
        self.request.refresh_from_db()

        self.assertEqual(self.request.status, LeaveRequest.Status.APPROVED)
        self.assertEqual(self.request.approver, self.manager_user)
        self.assertIsNotNone(self.request.decided_at)

        balance = self.assert_invariant(self.report)
        self.assertEqual(balance.used, Decimal(5))
        self.assertEqual(balance.pending, Decimal(0))
        # Approving does not consume more days — they were already held.
        self.assertEqual(balance.available, Decimal(25))

    def test_rejecting_releases_the_hold(self):
        reject_leave(leave_request=self.request, approver=self.hr_user, note="No cover.")
        self.request.refresh_from_db()

        self.assertEqual(self.request.status, LeaveRequest.Status.REJECTED)
        self.assertEqual(self.request.decision_note, "No cover.")

        balance = self.assert_invariant(self.report)
        self.assertEqual(balance.used, Decimal(0))
        self.assertEqual(balance.pending, Decimal(0))
        self.assertEqual(balance.available, Decimal(30))

    def test_a_request_cannot_be_decided_twice(self):
        approve_leave(leave_request=self.request, approver=self.hr_user)
        with self.assertRaises(ValidationError):
            approve_leave(leave_request=self.request, approver=self.hr_user)
        with self.assertRaises(ValidationError):
            reject_leave(leave_request=self.request, approver=self.hr_user)
        self.assert_invariant(self.report)

    def test_approving_without_permission_is_denied(self):
        with self.assertRaises(PermissionDenied):
            approve_leave(leave_request=self.request, approver=self.report_user)
        self.assertEqual(self.assert_invariant(self.report).pending, Decimal(5))

    def test_cancelling_a_pending_request_releases_the_hold(self):
        cancel_leave(leave_request=self.request, actor=self.report_user)
        self.request.refresh_from_db()

        self.assertEqual(self.request.status, LeaveRequest.Status.CANCELLED)
        balance = self.assert_invariant(self.report)
        self.assertEqual(balance.pending, Decimal(0))
        self.assertEqual(balance.available, Decimal(30))

    def test_cancelling_an_approved_request_returns_used_days(self):
        approve_leave(leave_request=self.request, approver=self.hr_user)
        cancel_leave(leave_request=self.request, actor=self.report_user)

        balance = self.assert_invariant(self.report)
        self.assertEqual(balance.used, Decimal(0))
        self.assertEqual(balance.available, Decimal(30))

    def test_a_manager_may_not_cancel_their_reports_request(self):
        """Rejecting is a manager's tool. Cancelling belongs to the owner."""
        with self.assertRaises(PermissionDenied):
            cancel_leave(leave_request=self.request, actor=self.manager_user)

    def test_leave_that_has_started_cannot_be_cancelled(self):
        LeaveRequest.objects.filter(pk=self.request.pk).update(
            start_date=timezone.localdate() - timedelta(days=1)
        )
        self.request.refresh_from_db()
        with self.assertRaises(ValidationError):
            cancel_leave(leave_request=self.request, actor=self.report_user)

    def test_the_full_lifecycle_leaves_the_balance_untouched(self):
        """apply -> reject -> apply -> approve -> cancel, back to 30."""
        reject_leave(leave_request=self.request, approver=self.hr_user)

        second = apply_leave(
            employee=self.report,
            leave_type=self.annual,
            start_date=self.start,
            end_date=self.start + timedelta(days=4),
        )
        approve_leave(leave_request=second, approver=self.hr_user)
        cancel_leave(leave_request=second, actor=self.report_user)

        balance = self.assert_invariant(self.report)
        self.assertEqual(balance.available, Decimal(30))
        self.assertEqual(balance.used, Decimal(0))
        self.assertEqual(balance.pending, Decimal(0))
