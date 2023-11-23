
from gymhero.models.exercise import Exercise, ExerciseType
from gymhero.crud.base import CRUDRepository


from gymhero.log import get_logger

log = get_logger(__name__)


exercise_crud = CRUDRepository(model=Exercise)
exercise_type_crud = CRUDRepository(model=ExerciseType)
