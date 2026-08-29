import logging

from django.db import transaction

from .middleware import get_current_request
from .models import AuditLog

logger = logging.getLogger(__name__)


def _client_ip(request):
    """
    The caller's real IP.

    Behind a proxy or load balancer, REMOTE_ADDR is the proxy. The original
    client is the first entry in X-Forwarded-For.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def snapshot(instance, fields):
    """
    Field values as plain strings, for before/after comparison.

    Everything is stringified because `changes` is a JSON column, and dates,
    Decimals and UUIDs are not JSON-serialisable on their own.
    """
    return {
        field: (None if getattr(instance, field, None) is None
                else str(getattr(instance, field)))
        for field in fields
    }


def diff(before, after):
    """
    Only what actually changed.

    Unchanged fields are left out on purpose. A log that records every
    field on every write is as unreadable as no log at all.
    """
    return {
        field: {"before": before.get(field), "after": after.get(field)}
        for field in after
        if before.get(field) != after.get(field)
    }


def log_action(*, action, instance, actor=None, changes=None):
    """
    Write one audit row.

    Never raises. An audit failure must not roll back the operation it was
    recording — losing a log line is bad; losing the approval it described
    is worse.
    """
    try:
        request = get_current_request()

        # Fall back to the logged-in user when the caller didn't name one.
        # Stays None for management commands and background jobs.
        if actor is None and request is not None:
            user = getattr(request, "user", None)
            if user is not None and user.is_authenticated:
                actor = user

        # A savepoint. If this INSERT fails inside a larger transaction,
        # only the savepoint rolls back — the surrounding approval survives.
        with transaction.atomic():
            AuditLog.objects.create(
                actor=actor,
                actor_label=getattr(actor, "email", "") or "system",
                action=action,
                model_name=instance.__class__.__name__,
                object_id=str(instance.pk),
                object_label=str(instance)[:255],
                changes=changes or {},
                ip_address=_client_ip(request) if request else None,
                user_agent=(
                    request.META.get("HTTP_USER_AGENT", "")[:500]
                    if request else ""
                ),
            )
    except Exception:
        logger.exception("Failed to write audit log for %r", instance)
