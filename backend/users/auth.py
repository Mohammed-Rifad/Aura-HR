def verified_user_rule(user):
    """
    User must be active and verified
    to authenticate or refresh tokens.
    """
    return (
        user is not None
        and user.is_active
        and user.is_verified
    )