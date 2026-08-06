"""
Clinical Telemetry & Medication Service.

Orchestrates medication regimens, TKI dosage adherence tracking, time-series vitals,
laboratory results (including BCR-ABL1 molecular responses), symptoms, and lifestyle logs.
"""

from typing import Optional, List, Tuple
import uuid

from sqlalchemy.orm import Session

from app.db.models.patient import PatientProfile
from app.db.models.medication import MedicationRegimen, MedicationAdherenceLog
from app.db.models.vitals import VitalSigns
from app.db.models.labs import LabResult
from app.db.models.symptoms import SymptomLog
from app.db.models.lifestyle import NutritionLog, LifestyleLog

from app.repositories.patient_repository import PatientRepository
from app.repositories.medication_repository import MedicationRepository
from app.repositories.clinical_repository import ClinicalRepository
from app.repositories.audit_repository import AuditLogRepository

from app.schemas.medication_schemas import (
    MedicationRegimenCreate,
    MedicationRegimenUpdate,
    MedicationAdherenceLogCreate,
    MedicationRegimenListResponse,
    MedicationRegimenRead,
)
from app.schemas.vitals_schemas import VitalSignsCreate, VitalSignsListResponse, VitalSignsRead
from app.schemas.labs_schemas import LabResultCreate, LabResultUpdate, LabResultListResponse, LabResultRead
from app.schemas.symptom_schemas import SymptomLogCreate, SymptomLogListResponse, SymptomLogRead
from app.schemas.lifestyle_schemas import (
    NutritionLogCreate,
    NutritionLogListResponse,
    NutritionLogRead,
    LifestyleLogCreate,
    LifestyleLogListResponse,
    LifestyleLogRead,
)
from app.schemas.auth_enums import UserRole
from app.core.exceptions import (
    ResourceNotFoundException,
    InsufficientPermissionError,
)


class ClinicalService:
    """Domain service for handling time-series physiological telemetry and clinical observations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.patient_repo = PatientRepository(db)
        self.medication_repo = MedicationRepository(db)
        self.clinical_repo = ClinicalRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def _verify_patient_access(
        self, patient_id: uuid.UUID, actor_id: int, actor_role: UserRole
    ) -> PatientProfile:
        """Private guard method validating actor authorization against a target patient record."""
        patient = self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise ResourceNotFoundException(f"Patient profile '{patient_id}' not found.")

        if actor_role == UserRole.PATIENT and patient.user_id != actor_id:
            raise InsufficientPermissionError("Access denied: You can only record/view telemetry for your own account.")

        return patient

    # -------------------------------------------------------------------------
    # Medication Regimen & Adherence Logic
    # -------------------------------------------------------------------------
    def add_medication_regimen(
        self,
        schema: MedicationRegimenCreate,
        actor_id: int,
        actor_role: UserRole,
        ip_address: Optional[str] = None,
    ) -> MedicationRegimen:
        """Prescribes a new TKI or supportive medication regimen for a patient."""
        self._verify_patient_access(schema.patient_id, actor_id, actor_role)

        if actor_role == UserRole.PATIENT:
            raise InsufficientPermissionError("Patients cannot self-prescribe medication regimens.")

        if not schema.prescribing_clinician_id:
            schema.prescribing_clinician_id = actor_id

        regimen = self.medication_repo.create_regimen(schema)

        self.audit_repo.log_event(
            user_id=actor_id,
            action="MEDICATION_REGIMEN_CREATED",
            resource=f"medication:{regimen.id}",
            status="SUCCESS",
            details={
                "patient_id": str(schema.patient_id),
                "medication_name": schema.medication_name,
                "dose": schema.dose,
            },
            ip_address=ip_address,
        )

        return regimen

    def log_medication_adherence(
        self,
        schema: MedicationAdherenceLogCreate,
        actor_id: int,
        actor_role: UserRole,
        ip_address: Optional[str] = None,
    ) -> MedicationAdherenceLog:
        """Logs an individual dosage administration event (taken or missed)."""
        regimen = self.medication_repo.get_regimen_by_id(schema.regimen_id)
        if not regimen:
            raise ResourceNotFoundException(f"Medication regimen '{schema.regimen_id}' not found.")

        self._verify_patient_access(regimen.patient_id, actor_id, actor_role)

        log_entry = self.medication_repo.log_adherence_event(schema)

        self.audit_repo.log_event(
            user_id=actor_id,
            action="MEDICATION_ADHERENCE_LOGGED",
            resource=f"adherence_log:{log_entry.id}",
            status="SUCCESS",
            details={
                "regimen_id": str(schema.regimen_id),
                "was_taken": schema.was_taken,
                "reason_missed": schema.reason_missed,
            },
            ip_address=ip_address,
        )

        return log_entry

    def get_patient_medications(
        self,
        patient_id: uuid.UUID,
        actor_id: int,
        actor_role: UserRole,
        active_only: bool = False,
    ) -> List[MedicationRegimenRead]:
        """Retrieves medication regimens prescribed for a patient."""
        self._verify_patient_access(patient_id, actor_id, actor_role)
        regimens = self.medication_repo.get_patient_regimens(patient_id, active_only=active_only)
        return [MedicationRegimenRead.model_validate(r) for r in regimens]

    # -------------------------------------------------------------------------
    # Vital Signs & Physiological Telemetry
    # -------------------------------------------------------------------------
    def record_vital_signs(
        self,
        schema: VitalSignsCreate,
        actor_id: int,
        actor_role: UserRole,
        ip_address: Optional[str] = None,
    ) -> VitalSignsRead:
        """Records time-series vital signs and automatically calculates BMI if height is available."""
        patient = self._verify_patient_access(schema.patient_id, actor_id, actor_role)

        calculated_bmi: Optional[float] = None
        if schema.weight_kg and patient.height_cm:
            # BMI Formula: weight (kg) / [height (m)]^2
            height_m = patient.height_cm / 100.0
            if height_m > 0:
                calculated_bmi = round(schema.weight_kg / (height_m ** 2), 2)

        vitals = self.clinical_repo.create_vitals(schema, bmi_calculated=calculated_bmi)

        self.audit_repo.log_event(
            user_id=actor_id,
            action="VITAL_SIGNS_RECORDED",
            resource=f"vitals:{vitals.id}",
            status="SUCCESS",
            details={"patient_id": str(schema.patient_id), "source": schema.measurement_source},
            ip_address=ip_address,
        )

        return VitalSignsRead.model_validate(vitals)

    def get_vitals_telemetry(
        self,
        patient_id: uuid.UUID,
        actor_id: int,
        actor_role: UserRole,
        page: int = 1,
        page_size: int = 20,
    ) -> VitalSignsListResponse:
        """Retrieves paginated historical vital signs records for chart visualization."""
        self._verify_patient_access(patient_id, actor_id, actor_role)
        items, total, pages = self.clinical_repo.get_vitals_history(patient_id, page=page, page_size=page_size)
        
        return VitalSignsListResponse(
            items=[VitalSignsRead.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    # -------------------------------------------------------------------------
    # Laboratory Results & Molecular Responses
    # -------------------------------------------------------------------------
    def record_lab_result(
        self,
        schema: LabResultCreate,
        actor_id: int,
        actor_role: UserRole,
        ip_address: Optional[str] = None,
    ) -> LabResultRead:
        """Records a laboratory test result or BCR-ABL1 quantitative PCR biomarker entry."""
        self._verify_patient_access(schema.patient_id, actor_id, actor_role)

        if actor_role == UserRole.PATIENT:
            raise InsufficientPermissionError("Patients cannot self-report laboratory test entries.")

        lab = self.clinical_repo.create_lab_result(schema)

        self.audit_repo.log_event(
            user_id=actor_id,
            action="LAB_RESULT_RECORDED",
            resource=f"lab:{lab.id}",
            status="SUCCESS",
            details={
                "patient_id": str(schema.patient_id),
                "test_name": schema.test_name,
                "numerical_value": schema.numerical_value,
            },
            ip_address=ip_address,
        )

        return LabResultRead.model_validate(lab)

    def get_patient_labs(
        self,
        patient_id: uuid.UUID,
        actor_id: int,
        actor_role: UserRole,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> LabResultListResponse:
        """Retrieves paginated laboratory results for a patient."""
        self._verify_patient_access(patient_id, actor_id, actor_role)
        items, total, pages = self.clinical_repo.get_labs_history(
            patient_id, category=category, page=page, page_size=page_size
        )

        return LabResultListResponse(
            items=[LabResultRead.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    # -------------------------------------------------------------------------
    # Symptom Logging & Lifestyle Telemetry
    # -------------------------------------------------------------------------
    def log_patient_symptom(
        self,
        schema: SymptomLogCreate,
        actor_id: int,
        actor_role: UserRole,
        ip_address: Optional[str] = None,
    ) -> SymptomLogRead:
        """Logs a patient-reported subjective symptom event."""
        self._verify_patient_access(schema.patient_id, actor_id, actor_role)
        symptom = self.clinical_repo.create_symptom_log(schema)

        self.audit_repo.log_event(
            user_id=actor_id,
            action="SYMPTOM_LOGGED",
            resource=f"symptom:{symptom.id}",
            status="SUCCESS",
            details={
                "patient_id": str(schema.patient_id),
                "symptom_name": schema.symptom_name,
                "severity": schema.severity,
            },
            ip_address=ip_address,
        )

        return SymptomLogRead.model_validate(symptom)

    def get_patient_symptoms(
        self,
        patient_id: uuid.UUID,
        actor_id: int,
        actor_role: UserRole,
        page: int = 1,
        page_size: int = 20,
    ) -> SymptomLogListResponse:
        """Retrieves paginated historical symptom logs."""
        self._verify_patient_access(patient_id, actor_id, actor_role)
        items, total, pages = self.clinical_repo.get_symptoms_history(patient_id, page=page, page_size=page_size)

        return SymptomLogListResponse(
            items=[SymptomLogRead.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    def log_daily_nutrition(
        self,
        schema: NutritionLogCreate,
        actor_id: int,
        actor_role: UserRole,
    ) -> NutritionLogRead:
        """Logs daily patient nutrition intake and meal tolerance."""
        self._verify_patient_access(schema.patient_id, actor_id, actor_role)
        entry = self.clinical_repo.create_nutrition_log(schema)
        return NutritionLogRead.model_validate(entry)

    def get_patient_nutrition(
        self,
        patient_id: uuid.UUID,
        actor_id: int,
        actor_role: UserRole,
        page: int = 1,
        page_size: int = 20,
    ) -> NutritionLogListResponse:
        """Retrieves paginated daily nutrition history."""
        self._verify_patient_access(patient_id, actor_id, actor_role)
        items, total, pages = self.clinical_repo.get_nutrition_history(patient_id, page=page, page_size=page_size)

        return NutritionLogListResponse(
            items=[NutritionLogRead.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    def log_daily_lifestyle(
        self,
        schema: LifestyleLogCreate,
        actor_id: int,
        actor_role: UserRole,
    ) -> LifestyleLogRead:
        """Logs daily activity, step count, sleep hours, and stress telemetry."""
        self._verify_patient_access(schema.patient_id, actor_id, actor_role)
        entry = self.clinical_repo.create_lifestyle_log(schema)
        return LifestyleLogRead.model_validate(entry)

    def get_patient_lifestyle(
        self,
        patient_id: uuid.UUID,
        actor_id: int,
        actor_role: UserRole,
        page: int = 1,
        page_size: int = 20,
    ) -> LifestyleLogListResponse:
        """Retrieves paginated daily lifestyle telemetry history."""
        self._verify_patient_access(patient_id, actor_id, actor_role)
        items, total, pages = self.clinical_repo.get_lifestyle_history(patient_id, page=page, page_size=page_size)

        return LifestyleLogListResponse(
            items=[LifestyleLogRead.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )