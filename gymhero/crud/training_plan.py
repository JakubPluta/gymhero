from sqlalchemy.orm import Session

from gymhero.crud.base import CRUDRepository
from gymhero.log import get_logger
from gymhero.models import TrainingPlan, TrainingUnit

log = get_logger(__name__)


class TrainingPlanCRUD(CRUDRepository):
    def add_training_unit_to_training_plan(
        self, db: Session, training_plan: TrainingPlan, training_unit: TrainingUnit
    ):
        """
        Adds a training unit to a training plan.

        Parameters:
            db (Session): The database session.
            training_plan (TrainingPlan): The training plan to add the training unit to.
            training_unit (TrainingUnit): The training unit to add.

        Returns:
            TrainingPlan: The updated training plan with the added training unit.
        """
        for existing_training_unit in training_plan.training_units:
            if existing_training_unit.id == training_unit.id:
                log.warning("Training unit already exists in training plan")
                return None

        training_plan.training_units.append(training_unit)
        db.add(training_plan)
        db.commit()
        db.refresh(training_plan)
        return training_plan

    def remove_training_unit_from_training_plan(
        self, db: Session, training_plan: TrainingPlan, training_unit: TrainingUnit
    ):
        """
        Removes a training unit from a training plan.

        Parameters:
            db (Session): The database session.
            training_plan (TrainingPlan): The training plan
                to remove the training unit from.
            training_unit (TrainingUnit): The training unit to remove.

        Returns:
            TrainingPlan: The updated training plan with the removed training unit.
        """
        try:
            training_plan.training_units.remove(training_unit)
        except ValueError:
            log.error("Training unit not found in training plan")
            return None

        db.add(training_plan)
        db.commit()
        db.refresh(training_plan)
        return training_plan

    def get_training_units_in_training_plan(self, training_plan: TrainingPlan):
        """
        Get the training units in a training plan.

        Parameters:
            training_plan (TrainingPlan): The training plan object.

        Returns:
            list: A list of training units in the training plan.
        """
        return training_plan.training_units


training_plan_crud = TrainingPlanCRUD(model=TrainingPlan)
