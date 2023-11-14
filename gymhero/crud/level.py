from typing import Optional, List

from gymhero.models.level import Level
from sqlalchemy.orm import Session
from gymhero.schemas.level import LevelCreate, LevelInDB, LevelUpdate
from logging import getLogger


log = getLogger(__name__)


def create_level(db: Session, level: LevelCreate) -> Level:
    log.info("creating level")
    level_data: dict = level.model_dump()
    level_orm: Level = Level(**level_data)
    db.add(level_orm)
    db.commit()
    db.refresh(level_orm)
    return level_orm


def get_all_levels(db: Session) -> List:
    return db.query(Level).all()


def get_level_by_id(db: Session, level_id: int) -> Optional[Level]:
    return db.query(Level).filter(Level.id == level_id).first()


def get_level_by_name(db: Session, level_name: str) -> Optional[Level]:
    return db.query(Level).filter(Level.name == level_name).first()


def delete_level(db: Session, level: Level) -> Level:
    db.delete(level),
    db.commit()
    return level


def update_level(db: Session, level: Level, update: LevelUpdate) -> Level:
    level.name = update.name
    level.key = update.name.lower().replace(" ", "_")
    db.add(level)
    db.commit()
    db.refresh(level)
    return level
