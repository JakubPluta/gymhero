from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.crud.base import CRUDRepository
from gymhero.log import get_logger
from gymhero.models import Exercise, TrainingUnit
from gymhero.models.training_unit import PrescribedSet, TrainingUnitExercise
from gymhero.schemas.training_unit import PrescriptionUpdate

log = get_logger(__name__)


class TrainingUnitCRUD(CRUDRepository[TrainingUnit]):
    async def add_exercise_to_training_unit(
        self, db: AsyncSession, training_unit: TrainingUnit, exercise: Exercise
    ) -> TrainingUnit | None:
        # Returns None if the exercise is already attached (caller maps that to 409).
        if self.get_link(training_unit, exercise.id) is not None:
            return None

        training_unit.exercises.append(TrainingUnitExercise(exercise_id=exercise.id))
        db.add(training_unit)
        await db.commit()
        await db.refresh(training_unit)
        return training_unit

    async def remove_exercise_from_training_unit(
        self, db: AsyncSession, training_unit: TrainingUnit, exercise: Exercise
    ) -> TrainingUnit:
        link = self.get_link(training_unit, exercise.id)
        if link is None:
            raise ValueError("Exercise not found in training unit")

        training_unit.exercises.remove(link)  # delete-orphan drops the row + its sets
        db.add(training_unit)
        await db.commit()
        await db.refresh(training_unit)
        return training_unit

    async def set_prescription(
        self,
        db: AsyncSession,
        link: TrainingUnitExercise,
        prescription: PrescriptionUpdate,
    ) -> TrainingUnitExercise:
        # Replace-all: delete-orphan drops the old sets, the new list is renumbered 1..N.
        link.sets = [
            PrescribedSet(set_number=i, reps=s.reps, weight=s.weight)
            for i, s in enumerate(prescription.sets, start=1)
        ]
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link

    def get_link(
        self, training_unit: TrainingUnit, exercise_id: int
    ) -> TrainingUnitExercise | None:
        for link in training_unit.exercises:
            if link.exercise_id == exercise_id:
                return link
        return None

    def get_exercises_in_training_unit(
        self, training_unit: TrainingUnit
    ) -> list[TrainingUnitExercise]:
        return list(training_unit.exercises)


training_unit_crud = TrainingUnitCRUD(model=TrainingUnit)
