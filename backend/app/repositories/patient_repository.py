"""
Patient Profile Repository.

Data access abstraction for PatientProfile entity creation, retrieval,
clinician assignment filtering, and paginated searches.
"""

import math
from typing import Optional, List, Tuple
import uuid

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.db.models.patient import PatientProfile
from app.schemas.patient_schemas import PatientCreate, PatientUpdate


class PatientRepository:
    """SQLAlchemy 2.0 repository for managing PatientProfile database records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, schema: PatientCreate) -> PatientProfile:
        """Instantiates and persists a new PatientProfile record."""
        patient = PatientProfile(**schema.model_dump())
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get_by_id(self, patient_id: uuid.UUID) -> Optional[PatientProfile]:
        """Fetches a patient profile by its unique UUID primary key."""
        stmt = select(PatientProfile).where(PatientProfile.id == patient_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_user_id(self, user_id: int) -> Optional[PatientProfile]:
        """Fetches a patient profile by its associated User account ID."""
        stmt = select(PatientProfile).where(PatientProfile.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_mrn(self, mrn: str) -> Optional[PatientProfile]:
        """Fetches a patient profile by Medical Record Number (MRN)."""
        stmt = select(PatientProfile).where(PatientProfile.medical_record_number == mrn)
        return self.db.execute(stmt).scalar_one_or_none()

    def update(self, patient: PatientProfile, schema: PatientUpdate) -> PatientProfile:
        """Applies partial schema updates to an existing PatientProfile record."""
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(patient, key, value)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def search_patients(
        self,
        query: Optional[str] = None,
        clinician_id: Optional[int] = None,
        disease_phase: Optional[str] = None,
        is_active: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[PatientProfile], int, int]:
        """
        Retrieves a paginated list of patient profiles filtered by search string,
        treating clinician ID, or CML disease phase.
        
        Returns:
            Tuple containing (items, total_count, total_pages)
        """
        stmt = select(PatientProfile).where(PatientProfile.is_active == is_active)

        if clinician_id is not None:
            stmt = stmt.where(PatientProfile.treating_physician_id == clinician_id)

        if disease_phase is not None:
            stmt = stmt.where(PatientProfile.disease_phase == disease_phase)

        if query:
            search_pattern = f"%{query.strip()}%"
            stmt = stmt.where(
                or_(
                    PatientProfile.first_name.ilike(search_pattern),
                    PatientProfile.last_name.ilike(search_pattern),
                    PatientProfile.medical_record_number.ilike(search_pattern),
                    PatientProfile.primary_diagnosis.ilike(search_pattern),
                )
            )

        # Count total matching records
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self.db.execute(count_stmt).scalar_one() or 0

        # Apply ordering and pagination
        stmt = stmt.order_by(PatientProfile.last_name.asc(), PatientProfile.first_name.asc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = list(self.db.execute(stmt).scalars().all())
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1

        return items, total_count, total_pages