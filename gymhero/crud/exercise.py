from gymhero.models.exercise import Exercise, ExerciseType
from gymhero.crud.base import CRUDRepository

exercise_crud = CRUDRepository(Exercise)
exercise_type_crud = CRUDRepository(ExerciseType)
