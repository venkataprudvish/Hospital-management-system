from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def get_user_role(user):
    """
    Return the authenticated user's application role.

    Returns None when the user is anonymous or has no Profile.
    """

    if not user or not user.is_authenticated:
        return None

    if getattr(user, "is_superuser", False):
        return "owner"

    profile = getattr(user, "profile", None)

    if profile is None:
        return None

    return profile.role


def has_role(user, *roles):
    """
    Check whether a user has one of the supplied application roles.

    Django superusers are treated as having full access.
    """

    if not user or not user.is_authenticated:
        return False

    if getattr(user, "is_superuser", False):
        return True

    role = get_user_role(user)

    return role in roles


def roles_required(*roles):
    """
    Decorator restricting a view to specific application roles.
    """

    def decorator(view_func):

        @login_required
        @wraps(view_func)
        def inner(request, *args, **kwargs):

            if has_role(request.user, *roles):
                return view_func(
                    request,
                    *args,
                    **kwargs,
                )

            raise PermissionDenied

        return inner

    return decorator