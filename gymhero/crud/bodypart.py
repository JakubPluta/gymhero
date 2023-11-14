from typing import Optional, List

from gymhero.models.exercise import BodyPart
from sqlalchemy.orm import Session
from gymhero.schemas.bodypart import BodyPartCreate, BodyPartUpdate
from logging import getLogger

log = getLogger(__name__)


def create_body_part(db: Session, body_part: BodyPartCreate) -> BodyPart:
    log.info("creating body part")
    body_part_data: dict = body_part.model_dump()
    body_part_orm: BodyPart = BodyPart(**body_part_data)
    db.add(body_part_orm)
    db.commit()
    db.refresh(body_part_orm)
    return body_part_orm


def get_all_body_parts(db: Session) -> List:
    return db.query(BodyPart).all()


def get_body_part_by_id(db: Session, body_part_id: int) -> Optional[BodyPart]:
    return db.query(BodyPart).filter(BodyPart.id == body_part_id).first()


def get_body_part_by_name(db: Session, body_part_name: str) -> Optional[BodyPart]:
    return db.query(BodyPart).filter(BodyPart.name == body_part_name).first()


def delete_body_part(db: Session, body_part: BodyPart) -> BodyPart:
    db.delete(body_part),
    db.commit()
    return body_part


def update_body_part(
        db: Session, body_part: BodyPart, body_part_update: BodyPartUpdate
) -> BodyPart:
    body_part.name = body_part_update.name
    body_part.key = body_part_update.name.lower().replace(" ", "_")
    db.add(body_part)
    db.commit()
    db.refresh(body_part)
    return body_part
