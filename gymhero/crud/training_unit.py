from sqlalchemy.orm import Session
from gymhero.crud.base import CRUDRepository
from gymhero.models import TrainingUnit
from gymhero.models import Exercise
from gymhero.log import get_logger


log = get_logger(__name__)


class TrainingUnitCRUD(CRUDRepository):
    def add_exercise_to_training_unit(
        self, db: Session, training_unit: TrainingUnit, exercise: Exercise
    ):
        """
        Adds an exercise to a training unit.

        Parameters:
            db (Session): The database session.
            training_unit (TrainingUnit): The training unit to add the exercise to.
            exercise (Exercise): The exercise to add.

        Returns:
            TrainingUnit: The updated training unit with the added exercise.
        """
        existing_exercise: Exercise
        for existing_exercise in training_unit.exercises:
            if existing_exercise.id == exercise.id:
                return None

        training_unit.exercises.append(exercise)
        db.add(training_unit)
        db.commit()
        db.refresh(training_unit)
        return training_unit

    def remove_exercise_from_training_unit(
        self, db: Session, training_unit: TrainingUnit, exercise: Exercise
    ):
        """
        Removes an exercise from a training unit.

        Parameters:
            db (Session): The database session.
            training_unit (TrainingUnit): The training unit to remove the exercise from.
            exercise (Exercise): The exercise to remove.

        Returns:
            TrainingUnit: The updated training unit with the removed exercise.
        """
        training_unit.exercises.remove(exercise)
        db.add(training_unit)
        db.commit()
        db.refresh(training_unit)
        return training_unit
