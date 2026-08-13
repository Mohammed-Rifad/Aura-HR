from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from common.permissions import IsAdmin

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
    UserSerializer,
)

User = get_user_model()


class LoginView(TokenObtainPairView):
    """
    POST email + password -> access token, refresh token, and the user.

    SimpleJWT does the work. We only swap in our serializer, which adds the
    role claim, the user payload, and the is_verified gate.
    """
    throttle_scope = "login"
    throttle_classes = [ScopedRateThrottle]

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

class UserAdminViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Account administration. Admin only.

    Deliberately not a ModelViewSet. Users are created through the admin,
    and destroy would hit Employee.user's PROTECT constraint. List, read,
    and flip the verification gate — that's the whole job.
    """

    queryset = User.objects.all().order_by("email")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    filterset_fields = ["role", "is_verified", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["email", "date_joined", "role"]

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """
        Clear an account for access.

        Idempotent — verifying an already-verified user returns 200, not an
        error. Actions like this get retried by flaky networks and impatient
        clicks; "already in the desired state" is success.
        """
        user = self.get_object()

        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])

        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=["post"])
    def unverify(self, request, pk=None):
        """Revoke access without touching the record."""
        user = self.get_object()

        # Without this an admin can lock themselves out, and if they're the
        # only admin, nobody left in the system can undo it.
        if user == request.user:
            raise ValidationError("You cannot unverify your own account.")

        if user.is_verified:
            user.is_verified = False
            user.save(update_fields=["is_verified"])

        return Response(self.get_serializer(user).data)


class LogoutView(generics.GenericAPIView):
    """POST the refresh token to blacklist it."""

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Logged out."})


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET  -> the logged-in user.
    PATCH -> update their own profile.

    No pk in the URL. get_object() returns request.user, so a user can only
    ever reach their own record. UserSerializer's read_only_fields stop them
    changing their role.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    """POST old_password + new_password."""

    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # get_serializer() passes the request in the context automatically,
        # which is how the serializer finds the current user.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated."})
