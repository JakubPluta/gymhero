from sqlalchemy.ext.asyncio import AsyncSession

from gymhero.crud.base import CRUDRepository
from gymhero.log import get_logger
from gymhero.models import TrainingPlan, TrainingUnit

log = get_logger(__name__)


class TrainingPlanCRUD(CRUDRepository[TrainingPlan]):
    async def add_training_unit_to_training_plan(
        self,
        db: AsyncSession,
        training_plan: TrainingPlan,
        training_unit: TrainingUnit,
    ) -> TrainingPlan | None:
        # Returns None if the unit is already attached (caller maps that to 409).
        for existing in training_plan.training_units:
            if existing.id == training_unit.id:
                return None

        training_plan.training_units.append(training_unit)
        db.add(training_plan)
        await db.commit()
        await db.refresh(training_plan)
        return training_plan

    async def remove_training_unit_from_training_plan(
        self,
        db: AsyncSession,
        training_plan: TrainingPlan,
        training_unit: TrainingUnit,
    ) -> TrainingPlan | None:
        # Returns None if the unit was not attached.
        try:
            training_plan.training_units.remove(training_unit)
        except ValueError:
            return None

        db.add(training_plan)
        await db.commit()
        await db.refresh(training_plan)
        return training_plan

    def get_training_units_in_training_plan(
        self, training_plan: TrainingPlan
    ) -> list[TrainingUnit]:
        return list(training_plan.training_units)


training_plan_crud = TrainingPlanCRUD(model=TrainingPlan)
