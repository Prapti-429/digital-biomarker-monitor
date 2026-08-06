"""
Medication Regimen Repository.

Data access abstraction for managing TKI medication regimens, updating
longitudinal adherence percentages, and recording dosage execution logs.
"""

import math
from typing import Optional, List, Tuple
import uuid

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models.medication import MedicationRegimen, MedicationAdherenceLog
from app.schemas.medication_schemas import (
    MedicationRegimenCreate,
    MedicationRegimenUpdate,
    MedicationAdherenceLogCreate,
)


class MedicationRepository:
    """SQLAlchemy 2.0 repository for managing MedicationRegimen and Adherence records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_regimen(self, schema: MedicationRegimenCreate) -> MedicationRegimen:
        """Creates a new prescribed medication regimen."""
        regimen = MedicationRegimen(**schema.model_dump())
        self.db.add(regimen)
        self.db.commit()
        self.db.refresh(regimen)
        return regimen

    def get_regimen_by_id(self, regimen_id: uuid.UUID) -> Optional[MedicationRegimen]:
        """Fetches a medication regimen by its UUID primary key."""
        stmt = select(MedicationRegimen).where(MedicationRegimen.id == regimen_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_patient_regimens(
        self, patient_id: uuid.UUID, active_only: bool = False
    ) -> List[MedicationRegimen]:
        """Retrieves all medication regimens associated with a patient."""
        stmt = select(MedicationRegimen).where(MedicationRegimen.patient_id == patient_id)
        if active_only:
            stmt = stmt.where(MedicationRegimen.is_active == True)
        stmt = stmt.order_by(MedicationRegimen.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def update_regimen(
        self, regimen: MedicationRegimen, schema: MedicationRegimenUpdate
    ) -> MedicationRegimen:
        """Applies partial updates to an existing medication regimen."""
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(regimen, key, value)
        self.db.commit()
        self.db.refresh(regimen)
        return regimen

    def log_adherence_event(
        self, schema: MedicationAdherenceLogCreate
    ) -> MedicationAdherenceLog:
        """Logs an individual dosage administration event and updates regimen statistics."""
        log_entry = MedicationAdherenceLog(**schema.model_dump())
        self.db.add(log_entry)
        
        # Fetch associated regimen to update adherence metrics
        regimen = self.get_regimen_by_id(schema.regimen_id)
        if regimen:
            if not schema.was_taken:
                regimen.missed_dose_counter += 1

            # Recalculate adherence percentage dynamically
            total_stmt = select(func.count(MedicationAdherenceLog.id)).where(
                MedicationAdherenceLog.regimen_id == schema.regimen_id
            )
            total_logs = (self.db.execute(total_stmt).scalar_one() or 0) + 1

            taken_stmt = select(func.count(MedicationAdherenceLog.id)).where(
                MedicationAdherenceLog.regimen_id == schema.regimen_id,
                MedicationAdherenceLog.was_taken == True,
            )
            taken_count = (self.db.execute(taken_stmt).scalar_one() or 0) + (
                1 if schema.was_taken else 0
            )

            regimen.adherence_percentage = round((taken_count / total_logs) * 100.0, 2)

        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def get_adherence_logs(
        self, regimen_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> Tuple[List[MedicationAdherenceLog], int, int]:
        """Retrieves paginated adherence event history for a given regimen."""
        stmt = select(MedicationAdherenceLog).where(
            MedicationAdherenceLog.regimen_id == regimen_id
        )
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self.db.execute(count_stmt).scalar_one() or 0

        stmt = stmt.order_by(MedicationAdherenceLog.scheduled_time.desc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = list(self.db.execute(stmt).scalars().all())
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1

        return items, total_count, total_pages