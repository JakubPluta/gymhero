from gymhero.models.exercise import Exercise, ExerciseType
from gymhero.crud.base import CRUDRepository

ExerciseCRUD = CRUDRepository(Exercise)
ExerciseTypeCRUD = CRUDRepository(ExerciseType)
