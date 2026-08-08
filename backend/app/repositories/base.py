"""
Generic Base Repository implementation for SQLAlchemy 2.x.
Provides thread-safe, transaction-aware CRUD, pagination, filtering, 
and sorting operations using Python Generics.
"""

import math
from enum import Enum
from typing import (
    Generic,
    TypeVar,
    Type,
    Optional,
    List,
    Dict,
    Any,
    Sequence,
    Union,
    Tuple,
)
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import select, update, delete, func, or_, and_, Tuple as SQLTuple
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Import ORM declarative base
from app.db.base import Base

# Type variables for Generic Repository
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortParam(BaseModel):
    field: str
    order: SortOrder = SortOrder.ASC


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (max(1, self.page) - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResult(Generic[ModelType]):
    def __init__(
        self,
        items: List[ModelType],
        total: int,
        page: int,
        page_size: int,
    ) -> None:
        self.items: List[ModelType] = items
        self.total: int = total
        self.page: int = page
        self.page_size: int = page_size
        self.pages: int = math.ceil(total / page_size) if page_size > 0 else 0
        self.has_next: bool = page < self.pages
        self.has_prev: bool = page > 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "pages": self.pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


# Custom Exception Hierarchy
class RepositoryError(Exception):
    """Base exception for all repository level operational errors."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.original_exception = original_exception


class EntityNotFoundError(RepositoryError):
    """Raised when an expected database record is not found."""

    def __init__(self, entity_name: str, identifier: Any) -> None:
        message = f"{entity_name} with identifier '{identifier}' was not found."
        super().__init__(message)
        self.entity_name = entity_name
        self.identifier = identifier


class DuplicateEntityError(RepositoryError):
    """Raised when a unique constraint violation occurs during creation/update."""

    def __init__(self, entity_name: str, details: str) -> None:
        message = f"{entity_name} creation failed due to duplicate entry constraint: {details}"
        super().__init__(message)
        self.entity_name = entity_name


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic Base Repository encapsulating SQLAlchemy 2.x ORM interactions.
    """

    def __init__(self, model: Type[ModelType], session: Session) -> None:
        self.model = model
        self.session = session

    def _get_entity_name(self) -> str:
        return self.model.__name__

    # -------------------------------------------------------------------------
    # Basic CRUD Operations
    # -------------------------------------------------------------------------

    def get_by_id(
        self,
        id_val: Any,
        options: Optional[Sequence[ORMOption]] = None,
        include_soft_deleted: bool = False,
    ) -> ModelType:
        """
        Fetch a single entity by primary key. Raises EntityNotFoundError if missing.
        """
        try:
            stmt = select(self.model).where(self.model.id == id_val)
            
            if hasattr(self.model, "is_deleted") and not include_soft_deleted:
                stmt = stmt.where(self.model.is_deleted == False)

            if options:
                stmt = stmt.options(*options)

            result = self.session.execute(stmt).scalar_one_or_none()
            if result is None:
                raise EntityNotFoundError(self._get_entity_name(), id_val)
            return result
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching {self._get_entity_name()} by ID: {str(e)}", e)

    def get_all(
        self,
        options: Optional[Sequence[ORMOption]] = None,
        include_soft_deleted: bool = False,
    ) -> List[ModelType]:
        """
        Retrieve all instances of the entity model.
        """
        try:
            stmt = select(self.model)
            if hasattr(self.model, "is_deleted") and not include_soft_deleted:
                stmt = stmt.where(self.model.is_deleted == False)
            if options:
                stmt = stmt.options(*options)
            result = self.session.execute(stmt).scalars().all()
            return list(result)
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error retrieving all {self._get_entity_name()} records", e)

    def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]], auto_commit: bool = True) -> ModelType:
        """
        Create and persist a new database entry.
        """
        try:
            if isinstance(obj_in, dict):
                create_data = obj_in
            else:
                create_data = obj_in.model_dump(exclude_unset=True)

            db_obj = self.model(**create_data)
            
            if hasattr(db_obj, "created_at") and getattr(db_obj, "created_at") is None:
                setattr(db_obj, "created_at", datetime.utcnow())

            self.session.add(db_obj)
            if auto_commit:
                self.session.commit()
                self.session.refresh(db_obj)
            else:
                self.session.flush()
            return db_obj
        except IntegrityError as e:
            self.session.rollback()
            raise DuplicateEntityError(self._get_entity_name(), str(e.orig))
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Error creating {self._get_entity_name()}", e)

    def update(
        self,
        id_val: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        auto_commit: bool = True,
    ) -> ModelType:
        """
        Update an existing entity by its ID.
        """
        db_obj = self.get_by_id(id_val)
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            if hasattr(db_obj, "updated_at"):
                setattr(db_obj, "updated_at", datetime.utcnow())

            self.session.add(db_obj)
            if auto_commit:
                self.session.commit()
                self.session.refresh(db_obj)
            else:
                self.session.flush()
            return db_obj
        except IntegrityError as e:
            self.session.rollback()
            raise DuplicateEntityError(self._get_entity_name(), str(e.orig))
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Error updating {self._get_entity_name()} ID {id_val}", e)

    def delete(self, id_val: Any, hard_delete: bool = False, auto_commit: bool = True) -> bool:
        """
        Remove an entity by ID (supports hard delete or soft delete if 'is_deleted' exists).
        """
        db_obj = self.get_by_id(id_val, include_soft_deleted=True)
        try:
            if hard_delete or not hasattr(db_obj, "is_deleted"):
                self.session.delete(db_obj)
            else:
                setattr(db_obj, "is_deleted", True)
                if hasattr(db_obj, "deleted_at"):
                    setattr(db_obj, "deleted_at", datetime.utcnow())
                self.session.add(db_obj)

            if auto_commit:
                self.session.commit()
            else:
                self.session.flush()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Error deleting {self._get_entity_name()} ID {id_val}", e)

    def exists(self, id_val: Any) -> bool:
        """
        Check if an entity with the given ID exists.
        """
        try:
            stmt = select(func.count(self.model.id)).where(self.model.id == id_val)
            if hasattr(self.model, "is_deleted"):
                stmt = stmt.where(self.model.is_deleted == False)
            count = self.session.execute(stmt).scalar()
            return (count or 0) > 0
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error checking existence for {self._get_entity_name()}", e)

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count total records matching specified filters.
        """
        try:
            stmt = select(func.count()).select_from(self.model)
            if hasattr(self.model, "is_deleted"):
                stmt = stmt.where(self.model.is_deleted == False)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        stmt = stmt.where(getattr(self.model, key) == value)

            return self.session.execute(stmt).scalar() or 0
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error counting {self._get_entity_name()} records", e)



    # -------------------------------------------------------------------------
    # Pagination, Filtering, & Sorting Operations
    # -------------------------------------------------------------------------

    def paginate(
        self,
        pagination: PaginationParams,
        filters: Optional[Dict[str, Any]] = None,
        sort_params: Optional[List[SortParam]] = None,
        options: Optional[Sequence[ORMOption]] = None,
    ) -> PaginatedResult[ModelType]:
        """
        Paginate query results with filters and explicit sorting parameters.
        """
        try:
            stmt = select(self.model)
            count_stmt = select(func.count()).select_from(self.model)

            # Soft delete filter
            if hasattr(self.model, "is_deleted"):
                stmt = stmt.where(self.model.is_deleted == False)
                count_stmt = count_stmt.where(self.model.is_deleted == False)

            # Apply dynamic equality filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        stmt = stmt.where(getattr(self.model, key) == value)
                        count_stmt = count_stmt.where(getattr(self.model, key) == value)

            # Execute total count
            total = self.session.execute(count_stmt).scalar() or 0

            # Apply multi-column sorting
            if sort_params:
                for sort_item in sort_params:
                    if hasattr(self.model, sort_item.field):
                        column = getattr(self.model, sort_item.field)
                        if sort_item.order == SortOrder.DESC:
                            stmt = stmt.order_by(column.desc())
                        else:
                            stmt = stmt.order_by(column.asc())
            else:
                if hasattr(self.model, "id"):
                    stmt = stmt.order_by(self.model.id.desc())

            # Apply pagination offset and limit
            stmt = stmt.offset(pagination.offset).limit(pagination.limit)

            if options:
                stmt = stmt.options(*options)

            items = self.session.execute(stmt).scalars().all()
            return PaginatedResult(
                items=list(items),
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
            )
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error executing pagination query on {self._get_entity_name()}", e)

    # -------------------------------------------------------------------------
    # Bulk Operations
    # -------------------------------------------------------------------------

    def bulk_create(
        self,
        objs_in: List[Union[CreateSchemaType, Dict[str, Any]]],
        auto_commit: bool = True,
    ) -> List[ModelType]:
        """
        Bulk insert multiple new entities.
        """
        try:
            db_objs: List[ModelType] = []
            for item in objs_in:
                data = item if isinstance(item, dict) else item.model_dump(exclude_unset=True)
                db_obj = self.model(**data)
                db_objs.append(db_obj)

            self.session.add_all(db_objs)
            if auto_commit:
                self.session.commit()
                for obj in db_objs:
                    self.session.refresh(obj)
            else:
                self.session.flush()
            return db_objs
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Error performing bulk create on {self._get_entity_name()}", e)

    def bulk_update(self, updates: List[Dict[str, Any]], auto_commit: bool = True) -> int:
        """
        Bulk update records by primary key dictionaries.
        """
        try:
            count = 0
            for update_data in updates:
                if "id" not in update_data:
                    continue
                id_val = update_data.pop("id")
                stmt = (
                    update(self.model)
                    .where(self.model.id == id_val)
                    .values(**update_data)
                )
                res = self.session.execute(stmt)
                count += res.rowcount

            if auto_commit:
                self.session.commit()
            else:
                self.session.flush()
            return count
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Error executing bulk update on {self._get_entity_name()}", e)

    def bulk_delete(self, ids: List[Any], auto_commit: bool = True) -> int:
        """
        Bulk delete records matching list of primary keys.
        """
        try:
            stmt = delete(self.model).where(self.model.id.in_(ids))
            res = self.session.execute(stmt)
            rowcount = res.rowcount

            if auto_commit:
                self.session.commit()
            else:
                self.session.flush()
            return rowcount
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(f"Error executing bulk delete on {self._get_entity_name()}", e)

    # -------------------------------------------------------------------------
    # Transaction Management Helpers
    # -------------------------------------------------------------------------

    def commit(self) -> None:
        try:
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError("Transaction commit failed", e)

    def rollback(self) -> None:
        self.session.rollback()

    def flush(self) -> None:
        self.session.flush()

    def refresh(self, obj: ModelType) -> None:
        self.session.refresh(obj)
