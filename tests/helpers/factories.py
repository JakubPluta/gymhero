import itertools

from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.models.body_part import BodyPart
from gymhero.models.exercise import Exercise, ExerciseType
from gymhero.models.level import Level
from gymhero.models.training_plan import TrainingPlan
from gymhero.models.training_unit import TrainingUnit, TrainingUnitExercise
from gymhero.models.user import User
from gymhero.security import get_password_hash

# Long enough for the registration strength rule (>= 8) so factory users can
# also log in through /auth.
DEFAULT_PASSWORD = "password123"

# Process-wide counter keeps emails/names unique across every row a test makes.
_counter = itertools.count(1)


def _unique(prefix: str) -> str:
    return f"{prefix}-{next(_counter)}"


async def _persist[T](db: AsyncSession, obj: T) -> T:
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def create_user(
    db: AsyncSession,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD,
    full_name: str | None = None,
    is_superuser: bool = False,
    is_active: bool = True,
) -> User:
    return await _persist(
        db,
        User(
            email=email or f"{_unique('user')}@example.com",
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_superuser=is_superuser,
            is_active=is_active,
        ),
    )


async def create_level(db: AsyncSession, *, name: str | None = None) -> Level:
    return await _persist(db, Level(name=name or _unique("Level")))


async def create_body_part(db: AsyncSession, *, name: str | None = None) -> BodyPart:
    return await _persist(db, BodyPart(name=name or _unique("BodyPart")))


async def create_exercise_type(
    db: AsyncSession, *, name: str | None = None
) -> ExerciseType:
    return await _persist(db, ExerciseType(name=name or _unique("ExerciseType")))


async def create_exercise(
    db: AsyncSession,
    *,
    owner: User,
    name: str | None = None,
    description: str | None = None,
    body_part: BodyPart | None = None,
    level: Level | None = None,
    exercise_type: ExerciseType | None = None,
) -> Exercise:
    body_part = body_part or await create_body_part(db)
    level = level or await create_level(db)
    exercise_type = exercise_type or await create_exercise_type(db)
    return await _persist(
        db,
        Exercise(
            name=name or _unique("Exercise"),
            description=description,
            target_body_part_id=body_part.id,
            exercise_type_id=exercise_type.id,
            level_id=level.id,
            owner_id=owner.id,
        ),
    )


async def create_training_unit(
    db: AsyncSession,
    *,
    owner: User,
    name: str | None = None,
    description: str | None = None,
    exercises: list[Exercise] | None = None,
) -> TrainingUnit:
    unit = TrainingUnit(
        name=name or _unique("unit"), description=description, owner_id=owner.id
    )
    if exercises:
        unit.exercises = [TrainingUnitExercise(exercise=e) for e in exercises]
    return await _persist(db, unit)


async def create_training_plan(
    db: AsyncSession,
    *,
    owner: User,
    name: str | None = None,
    description: str | None = None,
    training_units: list[TrainingUnit] | None = None,
) -> TrainingPlan:
    plan = TrainingPlan(
        name=name or _unique("plan"), description=description, owner_id=owner.id
    )
    if training_units:
        plan.training_units = training_units
    return await _persist(db, plan)
