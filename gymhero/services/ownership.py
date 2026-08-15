"""Owner-scoped fetch shared by owner-private resources (training units/plans)."""

from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.crud.base import CRUDRepository
from gymhero.database.base_class import Base
from gymhero.exceptions import EntityNotFoundError
from gymhero.models.user import User


async def get_owned_or_404[ModelT: Base](
    db: AsyncSession,
    *,
    crud: CRUDRepository[ModelT],
    model: type[ModelT],
    entity_id: int,
    actor: User,
    entity: str,
) -> ModelT:
    """Fetch an owner-private resource the actor may access, else 404.

    Non-owners get 404 (not 403) so the API never reveals that a resource they
    cannot access exists. Superusers are unscoped and see everything.
    """
    scope: dict[str, int] = {} if actor.is_superuser else {"owner_id": actor.id}
    # `model.id` is a mapped column resolved at runtime (no static SA plugin here).
    obj = await crud.get_one(db, model.id == entity_id, **scope)  # type: ignore[attr-defined]
    if obj is None:
        raise EntityNotFoundError(f"{entity} with id {entity_id} not found")
    return obj
