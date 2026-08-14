from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.crud.base import CRUDRepository
from gymhero.log import get_logger
from gymhero.models import Exercise, TrainingUnit

log = get_logger(__name__)


class TrainingUnitCRUD(CRUDRepository[TrainingUnit]):
    async def add_exercise_to_training_unit(
        self, db: AsyncSession, training_unit: TrainingUnit, exercise: Exercise
    ) -> TrainingUnit | None:
        # Returns None if the exercise is already attached (caller maps that to 409).
        for existing in training_unit.exercises:
            if existing.id == exercise.id:
                return None

        training_unit.exercises.append(exercise)
        db.add(training_unit)
        await db.commit()
        await db.refresh(training_unit)
        return training_unit

    async def remove_exercise_from_training_unit(
        self, db: AsyncSession, training_unit: TrainingUnit, exercise: Exercise
    ) -> TrainingUnit:
        try:
            training_unit.exercises.remove(exercise)
        except ValueError as ve:
            raise ValueError("Exercise not found in training unit") from ve

        db.add(training_unit)
        await db.commit()
        await db.refresh(training_unit)
        return training_unit

    def get_exercises_in_training_unit(
        self, training_unit: TrainingUnit
    ) -> list[Exercise]:
        return list(training_unit.exercises)

    def check_if_exercise_in_training_unit(
        self, training_unit: TrainingUnit, exercise: Exercise
    ) -> bool:
        return exercise in training_unit.exercises


training_unit_crud = TrainingUnitCRUD(model=TrainingUnit)
