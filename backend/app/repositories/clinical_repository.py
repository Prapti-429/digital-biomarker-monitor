"""
Unified Clinical Telemetry Repository.

Provides data access methods for time-series vital signs, laboratory test entries
(including CML BCR-ABL PCR results), symptom tracking logs, and lifestyle/nutrition logs.
"""

import math
from typing import Optional, List, Tuple
import uuid

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models.vitals import VitalSigns
from app.db.models.labs import LabResult
from app.db.models.symptoms import SymptomLog
from app.db.models.lifestyle import NutritionLog, LifestyleLog
from app.schemas.vitals_schemas import VitalSignsCreate
from app.schemas.labs_schemas import LabResultCreate, LabResultUpdate
from app.schemas.symptom_schemas import SymptomLogCreate
from app.schemas.lifestyle_schemas import NutritionLogCreate, LifestyleLogCreate


class ClinicalRepository:
    """SQLAlchemy 2.0 repository for managing longitudinal clinical telemetry."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # -------------------------------------------------------------------------
    # Vital Signs Methods
    # -------------------------------------------------------------------------
    def create_vitals(self, schema: VitalSignsCreate, bmi_calculated: Optional[float] = None) -> VitalSigns:
        """Persists a new vital signs telemetry record."""
        data = schema.model_dump()
        if bmi_calculated is not None:
            data["bmi"] = bmi_calculated

        vitals = VitalSigns(**data)
        self.db.add(vitals)
        self.db.commit()
        self.db.refresh(vitals)
        return vitals

    def get_vitals_history(
        self, patient_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> Tuple[List[VitalSigns], int, int]:
        """Retrieves paginated historical vital signs records for a patient."""
        stmt = select(VitalSigns).where(VitalSigns.patient_id == patient_id)
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self.db.execute(count_stmt).scalar_one() or 0

        stmt = stmt.order_by(VitalSigns.recorded_at.desc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = list(self.db.execute(stmt).scalars().all())
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1

        return items, total_count, total_pages

    # -------------------------------------------------------------------------
    # Laboratory & Biomarker Methods
    # -------------------------------------------------------------------------
    def create_lab_result(self, schema: LabResultCreate) -> LabResult:
        """Persists a new clinical laboratory result or molecular biomarker entry."""
        lab_entry = LabResult(**schema.model_dump())
        self.db.add(lab_entry)
        self.db.commit()
        self.db.refresh(lab_entry)
        return lab_entry

    def get_lab_result_by_id(self, lab_id: uuid.UUID) -> Optional[LabResult]:
        """Fetches a single lab result record by its primary key."""
        stmt = select(LabResult).where(LabResult.id == lab_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def update_lab_result(self, lab_entry: LabResult, schema: LabResultUpdate) -> LabResult:
        """Updates an existing laboratory record."""
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(lab_entry, key, value)
        self.db.commit()
        self.db.refresh(lab_entry)
        return lab_entry

    def get_labs_history(
        self,
        patient_id: uuid.UUID,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[LabResult], int, int]:
        """Retrieves paginated laboratory results for a patient, optionally filtered by category."""
        stmt = select(LabResult).where(LabResult.patient_id == patient_id)
        
        if category:
            stmt = stmt.where(LabResult.test_category == category)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self.db.execute(count_stmt).scalar_one() or 0

        stmt = stmt.order_by(LabResult.collection_date.desc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = list(self.db.execute(stmt).scalars().all())
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1

        return items, total_count, total_pages

    # -------------------------------------------------------------------------
    # Symptom Logs Methods
    # -------------------------------------------------------------------------
    def create_symptom_log(self, schema: SymptomLogCreate) -> SymptomLog:
        """Persists a new subjective symptom log entry."""
        symptom = SymptomLog(**schema.model_dump())
        self.db.add(symptom)
        self.db.commit()
        self.db.refresh(symptom)
        return symptom

    def get_symptoms_history(
        self, patient_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> Tuple[List[SymptomLog], int, int]:
        """Retrieves paginated historical symptom reports for a patient."""
        stmt = select(SymptomLog).where(SymptomLog.patient_id == patient_id)
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self.db.execute(count_stmt).scalar_one() or 0

        stmt = stmt.order_by(SymptomLog.recorded_at.desc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = list(self.db.execute(stmt).scalars().all())
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1

        return items, total_count, total_pages

    # -------------------------------------------------------------------------
    # Nutrition & Lifestyle Methods
    # -------------------------------------------------------------------------
    def create_nutrition_log(self, schema: NutritionLogCreate) -> NutritionLog:
        """Persists a new daily nutrition tracking entry."""
        log_entry = NutritionLog(**schema.model_dump())
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def get_nutrition_history(
        self, patient_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> Tuple[List[NutritionLog], int, int]:
        """Retrieves paginated daily nutrition history for a patient."""
        stmt = select(NutritionLog).where(NutritionLog.patient_id == patient_id)
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self.db.execute(count_stmt).scalar_one() or 0

        stmt = stmt.order_by(NutritionLog.log_date.desc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = list(self.db.execute(stmt).scalars().all())
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1

        return items, total_count, total_pages

    def create_lifestyle_log(self, schema: LifestyleLogCreate) -> LifestyleLog:
        """Persists a new daily lifestyle/activity entry."""
        log_entry = LifestyleLog(**schema.model_dump())
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def get_lifestyle_history(
        self, patient_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> Tuple[List[LifestyleLog], int, int]:
        """Retrieves paginated lifestyle telemetry history for a patient."""
        stmt = select(LifestyleLog).where(LifestyleLog.patient_id == patient_id)
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self.db.execute(count_stmt).scalar_one() or 0

        stmt = stmt.order_by(LifestyleLog.log_date.desc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = list(self.db.execute(stmt).scalars().all())
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1

        return items, total_count, total_pages