"""
This module contains the base interface for CRUD 
(Create, Read, Update, Delete) operations.
"""
from typing import List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from gymhero.log import get_logger

ORMModel = TypeVar("ORMModel")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
OwnerIDType = int

log = get_logger(__name__)


class CRUDRepository:
    """Base interface for CRUD operations."""

    def __init__(self, model: Type[ORMModel]) -> None:
        """Initialize the CRUD repository.

        Parameters:
            model (Type[ORMModel]): The ORM model to use for CRUD operations.
            To see models go to gymhero.models module.
        """
        self._model = model
        self._name = model.__name__

    def get_one(self, db: Session, *args, **kwargs) -> Optional[ORMModel]:
        """
        Retrieves one record from the database.

        Parameters:
            db (Session): The database session object.
            *args: Variable length argument list used for filter
                e.g. filter(MyClass.name == 'some name')
            **kwargs: Keyword arguments used for filter_by e.g.
                filter_by(name='some name')

        Returns:
            Optional[ORMModel]: The retrieved record, if found.
        """
        log.debug(
            "retrieving one record for %s",
            self._model.__name__,
        )
        return db.query(self._model).filter(*args).filter_by(**kwargs).first()

    def get_many(
        self, db: Session, *args, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[ORMModel]:
        """
        Retrieves multiple records from the database.

        Parameters:
            db (Session): The database session.
            *args: Variable number of arguments. For example: filter
                db.query(MyClass).filter(MyClass.name == 'some name', MyClass.id > 5)
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to retrieve.
                Defaults to 100.
            **kwargs: Variable number of keyword arguments. For example: filter_by
                db.query(MyClass).filter_by(name='some name', id > 5)

        Returns:
            List[ORMModel]: List of retrieved records.
        """
        log.debug(
            "retrieving many records for %s with pagination skip %s and limit %s",
            self._model.__name__,
            skip,
            limit,
        )
        return (
            db.query(self._model)
            .filter(*args)
            .filter_by(**kwargs)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, obj_create: CreateSchemaType) -> ORMModel:
        """
        Create a new record in the database.

        Parameters:
            db (Session): The database session.
            obj_create (CreateModelType): The data for creating the new record.
            It's a pydantic BaseModel

        Returns:
            ORMModel: The newly created record.
        """
        log.debug(
            "creating record for %s with data %s",
            str(self._model.__name__),
            obj_create.model_dump(),
        )
        obj_create_data = obj_create.model_dump(exclude_none=True, exclude_unset=True)
        db_obj = self._model(**obj_create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ORMModel,
        obj_update: UpdateSchemaType,
    ) -> ORMModel:
        """
        Updates a record in the database.

        Parameters:
            db (Session): The database session.
            db_obj (ORMModel): The database object to be updated.
            obj_update (UpdateModelType): The updated data for the object
                - it's a pydantic BaseModel.

        Returns:
            ORMModel: The updated database object.
        """
        log.debug(
            "updating record for %s with data %s",
            self._model.__name__,
            obj_update.model_dump(),
        )
        obj_update_data = obj_update.model_dump(
            exclude_unset=True
        )  # exclude_unset=True -
        # do not update fields with None
        for field, value in obj_update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: ORMModel) -> ORMModel:
        """
        Deletes a record from the database.

        Parameters:
            db (Session): The database session.
            db_obj (ORMModel): The object to be deleted from the database.

        Returns:
            ORMModel: The deleted object.

        """
        log.debug("deleting record for %s with id %s", self._model.__name__, db_obj.id)
        db.delete(db_obj)
        db.commit()
        return db_obj

    def create_with_owner(
        self, db: Session, obj_create: CreateSchemaType, owner_id: OwnerIDType
    ) -> ORMModel:
        """Create a new record with ownerin the database.

        Parameters:
            db (Session): The database session.
            owner_id (int): The id of the owner of the record.
            obj_create (CreateSchemaType): Pydantic model for given schema

        Returns:
            ORMModel: The newly created record.
        """
        log.debug(
            "creating record for %s with data %s",
            self._model.__name__,
            obj_create.model_dump(),
        )
        obj_create_data = obj_create.model_dump(
            exclude_none=True, exclude_unset=True, exclude_defaults=True
        )
        db_obj = self._model(**obj_create_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_many_for_owner(
        self,
        db: Session,
        *args,
        owner_id: OwnerIDType,
        skip: int = 0,
        limit: int = 100,
        **kwargs
    ) -> List[ORMModel]:
        """
        Fetches multiple records for a specific owner.

        Parameters:
            db (Session): The database session.
            *args: Variable length argument list.
            owner_id (int): The id of the owner.
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to fetch.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            List[ORMModel]: A list of the fetched records.

        """
        return self.get_many(
            db, *args, skip=skip, limit=limit, owner_id=owner_id, **kwargs
        )
