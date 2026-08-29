import contextvars

# Holds the request for the duration of one request/response cycle.
# contextvars, not threading.local — this stays correct under async views,
# where one thread handles many requests at once.
_current_request = contextvars.ContextVar("current_request", default=None)


def get_current_request():
    """The request being handled right now, or None outside a request."""
    return _current_request.get()


class AuditContextMiddleware:
    """
    Makes the current request reachable from anywhere, so audit logging can
    record the IP without every service function taking a `request` argument.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = _current_request.set(request)
        try:
            return self.get_response(request)
        finally:
            # Always reset. Without this the value survives into the next
            # request this worker handles, and you log the wrong person's IP.
            _current_request.reset(token)
