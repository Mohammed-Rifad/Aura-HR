from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    The shape of a user everywhere the API returns one — /me, login
    responses, and later as a nested object on Employee.
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "profile_picture",
            "is_verified",
            "date_joined",
            "last_login",
        ]
        # Anything a user must not be able to change about themselves.
        # `role` in particular: without it here, any employee could PATCH
        # /me with {"role": "ADMIN"} and promote themselves.
        read_only_fields = [
            "id",
            "email",
            "role",
            "is_verified",
            "date_joined",
            "last_login",
        ]

    def get_full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class LoginSerializer(TokenObtainPairSerializer):
    """
    Login. Extends SimpleJWT so we keep its credential checking and add
    two things the default response doesn't give us.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claims baked into the JWT. These exist so the frontend can render
        # role-appropriate navigation without a second request.
        #
        # They are NOT an authorization source. A claim reflects state at
        # issue time — demote someone from HR and their existing token still
        # says HR until it expires. Server-side checks read request.user.role
        # from the database, always.
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        # super() checks the credentials, rejects inactive users, populates
        # self.user, and returns {"access": ..., "refresh": ...}.
        data = super().validate(attrs)

        # is_verified is a gate: an account exists but isn't cleared for
        # access until HR verifies it. AuthenticationFailed (401) rather
        # than ValidationError (400) — the request was well-formed, the
        # caller just isn't allowed to authenticate.
        #
        # This message deliberately confirms the account exists. That is a
        # user-enumeration trade-off we can afford because accounts are
        # created by HR, not by public self-signup, so an attacker has no
        # way to register probes. Swap it for a generic "invalid
        # credentials" if signup ever opens up.
        if not self.user.is_verified:
            raise AuthenticationFailed(
                "This account has not been verified yet. Contact HR.",
                code="account_not_verified",
            )

        # Attach the user so the client doesn't need a follow-up /me call.
        data["user"] = UserSerializer(self.user).data
        return data


class PasswordChangeSerializer(serializers.Serializer):
    """
    Not a ModelSerializer — we aren't creating or updating a model from
    these fields, we're running an action. `password` is never read back,
    so both fields are write-only.
    """

    old_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        # Runs the new password through AUTH_PASSWORD_VALIDATORS from
        # settings. Passing the user lets UserAttributeSimilarityValidator
        # reject passwords derived from their own email or name.
        validate_password(value, self.context["request"].user)
        return value

    def validate(self, attrs):
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must differ from the current one."}
            )
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        # set_password() hashes. Assigning user.password directly would
        # store the plaintext and silently break every future login.
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class LogoutSerializer(serializers.Serializer):
    """
    Takes the refresh token and blacklists it.

    Access tokens can't be revoked — they're validated by signature alone,
    with nothing stored server-side. So logout kills the refresh token, and
    the access token dies on its own when it expires (30 minutes).
    """

    refresh = serializers.CharField(write_only=True)

    def validate_refresh(self, value):
        try:
            self.token = RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError("Token is invalid or expired.")
        return value

    def save(self, **kwargs):
        self.token.blacklist()
