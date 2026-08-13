"""Centralized authorization rules.

A single, unit-testable home for ownership checks. Previously this logic was
copy-pasted into every owner-scoped route as
``if resource.owner_id != user.id and not user.is_superuser`` — a pattern that
silently regressed in ``exercise.py`` (``or`` instead of ``and``). Keeping it
here means the policy is defined and tested exactly once.
"""

from typing import Protocol

from gymhero.exceptions import PermissionDeniedError
from gymhero.models.user import User

_DEFAULT_MESSAGE = "The user does not have enough privileges"


class SupportsOwnership(Protocol):
    """Any ORM entity that has an ``owner_id`` column."""

    owner_id: int


def authorize_owner_or_superuser(
    resource: SupportsOwnership,
    actor: User,
    *,
    message: str = _DEFAULT_MESSAGE,
) -> None:
    """Permit the action only if ``actor`` owns ``resource`` or is a superuser.

    Args:
        resource: The owned entity being acted upon.
        actor: The authenticated user performing the action.
        message: Detail surfaced to the client on denial.

    Raises:
        PermissionDeniedError: If the actor is neither owner nor superuser.
    """
    if actor.is_superuser or resource.owner_id == actor.id:
        return
    raise PermissionDeniedError(message)
