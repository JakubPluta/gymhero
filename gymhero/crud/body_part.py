from gymhero.crud.base import CRUDRepository
from gymhero.models.body_part import BodyPart

bodypart_crud: CRUDRepository[BodyPart] = CRUDRepository(model=BodyPart)
