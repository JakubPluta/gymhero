from typing import Any, Dict

from sqlalchemy import MetaData
from sqlalchemy.orm import as_declarative

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class_registry: Dict[str, Any] = {}


@as_declarative(class_registry=class_registry)
class Base:
    id: Any
    __name__: str
    __abstract__: bool = True
    metadata = metadata
