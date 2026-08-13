import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def _normalise_detail(detail):
    """
    Flatten DRF's error detail into {field: [messages]} plus a top-level message.

    DRF returns wildly different shapes depending on the exception: a bare
    string, a list, or a nested dict of lists. The frontend shouldn't have to
    branch on all three.
    """
    if isinstance(detail, dict):
        errors = {
            key: value if isinstance(value, list) else [str(value)]
            for key, value in detail.items()
        }
        first_key = next(iter(errors), None)
        message = errors[first_key][0] if first_key else "Request failed."
        return message, errors

    if isinstance(detail, list):
        messages = [str(item) for item in detail]
        return (messages[0] if messages else "Request failed."), {"detail": messages}

    return str(detail), {"detail": [str(detail)]}


def api_exception_handler(exc, context):
    """
    Return a single, predictable error shape for every failure:

        {
          "success": false,
          "message": "Human-readable summary",
          "errors": {"field": ["..."]},
          "code": "validation_error"
        }

    Successful responses stay as plain DRF payloads — wrapping those too would
    fight pagination and drf-spectacular for no real gain. Errors are where
    shape consistency actually saves the frontend work.
    """
    # Translate Django-native exceptions into their DRF equivalents so they
    # don't escape as unhandled 500s.
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        # Carry the original message across. Constructing a bare
        # PermissionDenied() would replace a specific reason ("You are not
        # allowed to decide this request.") with DRF's generic default.
        exc = exceptions.PermissionDenied(exc.args[0] if exc.args else None)
    elif isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    response = drf_exception_handler(exc, context)

    if response is None:
        # Genuinely unexpected — log it with the request for debugging, and
        # never leak the traceback to the client.
        request = context.get("request")
        logger.exception(
            "Unhandled exception on %s %s",
            getattr(request, "method", "?"),
            getattr(request, "path", "?"),
        )
        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred.",
                "errors": {"detail": ["Internal server error."]},
                "code": "server_error",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    message, errors = _normalise_detail(response.data)

    response.data = {
        "success": False,
        "message": message,
        "errors": errors,
        "code": getattr(exc.detail, "code", None) or getattr(exc, "default_code", "error"),        
    }
    return response
