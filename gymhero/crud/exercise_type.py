from gymhero.crud.base import CRUDRepository
from gymhero.log import get_logger
from gymhero.models.exercise import ExerciseType

log = get_logger(__name__)

exercise_type_crud = CRUDRepository(model=ExerciseType)
