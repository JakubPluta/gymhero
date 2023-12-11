from typing import List

from sqlalchemy.orm import Session

from gymhero.crud.base import CRUDRepository
from gymhero.log import get_logger
from gymhero.models import Exercise, TrainingUnit

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
                log.warning("Exercise already exists in training unit")
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
        try:
            training_unit.exercises.remove(exercise)
        except ValueError as ve:
            log.error("Exercise not found in training unit")
            raise ValueError("Exercise not found in training unit") from ve

        db.add(training_unit)
        db.commit()
        db.refresh(training_unit)
        return training_unit

    def get_exercises_in_training_unit(
        self, training_unit: TrainingUnit
    ) -> List[Exercise]:
        """Returns a list of exercises in a training unit.

        Parameters:
            training_unit (TrainingUnit): The training unit to get the exercises from.

        Returns:
            List[Exercise]: A list of exercises in the training unit.
        """
        return training_unit.exercises

    def check_if_exercise_in_training_unit(
        self, training_unit: TrainingUnit, exercise: Exercise
    ) -> bool:
        """Checks if an exercise is in a training unit.

        Parameters:
            training_unit (TrainingUnit): The training unit to check.
            exercise (Exercise): The exercise to check.

        Returns:
            bool: True if the exercise is in the training unit, False otherwise.
        """
        return exercise in training_unit.exercises


training_unit_crud = TrainingUnitCRUD(model=TrainingUnit)
