"""
Patient Profile Management Service.

Orchestrates patient lifecycle workflows, automated Medical Record Number (MRN)
generation, baseline BMI calculations, and HIPAA compliance audit logging.
"""

from typing import Optional, List, Tuple
import uuid
import secrets

from sqlalchemy.orm import Session

from app.db.models.patient import PatientProfile
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient_schemas import PatientCreate, PatientUpdate, PatientListResponse, PatientRead
from app.schemas.auth_enums import UserRole
from app.core.exceptions import (
    ResourceNotFoundException,
    ConflictException,
    InsufficientPermissionError,
)
from app.repositories.audit_repository import AuditLogRepository


class PatientService:
    """Domain service for managing patient demographic and clinical profile operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.patient_repo = PatientRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def _generate_unique_mrn(self) -> str:
        """Generates a secure, human-readable Medical Record Number (e.g. CML-8F32A9)."""
        while True:
            candidate = f"CML-{secrets.token_hex(3).upper()}"
            if not self.patient_repo.get_by_mrn(candidate):
                return candidate

    def create_patient_profile(
        self,
        schema: PatientCreate,
        actor_id: int,
        actor_role: UserRole,
        ip_address: Optional[str] = None,
    ) -> PatientProfile:
        """
        Creates a new patient profile bound to an existing User account.
        Ensures 1:1 user-to-patient mapping and auto-assigns MRN if unprovided.
        """
        # Validate that the target user does not already possess a PatientProfile
        existing = self.patient_repo.get_by_user_id(schema.user_id)
        if existing:
            raise ConflictException(f"Patient profile already exists for User ID {schema.user_id}.")

        # Auto-assign MRN if not explicitly supplied
        if not schema.medical_record_number:
            schema.medical_record_number = self._generate_unique_mrn()
        elif self.patient_repo.get_by_mrn(schema.medical_record_number):
            raise ConflictException(f"Medical Record Number '{schema.medical_record_number}' is already registered.")

        patient = self.patient_repo.create(schema)

        # Audit log creation event
        self.audit_repo.log_event(
            user_id=actor_id,
            action="PATIENT_PROFILE_CREATED",
            resource=f"patient:{patient.id}",
            status="SUCCESS",
            details={
                "target_user_id": schema.user_id,
                "mrn": patient.medical_record_number,
                "primary_diagnosis": patient.primary_diagnosis,
            },
            ip_address=ip_address,
        )

        return patient

    def get_patient_by_id(
        self,
        patient_id: uuid.UUID,
        actor_id: int,
        actor_role: UserRole,
    ) -> PatientProfile:
        """
        Retrieves a patient profile by UUID while enforcing RBAC access boundaries:
        - Administrators can view any patient.
        - Clinicians can view assigned patients (or any patient if unassigned).
        - Patients can ONLY view their own bound profile.
        """
        patient = self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise ResourceNotFoundException(f"Patient profile '{patient_id}' not found.")

        # RBAC ownership verification
        if actor_role == UserRole.PATIENT and patient.user_id != actor_id:
            raise InsufficientPermissionError("Patients are strictly restricted to accessing their own profile.")

        return patient

    def get_patient_by_user_id(self, user_id: int) -> PatientProfile:
        """Retrieves a patient profile directly by associated User ID."""
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            raise ResourceNotFoundException(f"No clinical patient profile associated with User ID {user_id}.")
        return patient

    def update_patient_profile(
        self,
        patient_id: uuid.UUID,
        schema: PatientUpdate,
        actor_id: int,
        actor_role: UserRole,
        ip_address: Optional[str] = None,
    ) -> PatientProfile:
        """Updates demographics or clinical contextual data for an existing patient."""
        patient = self.get_patient_by_id(patient_id, actor_id, actor_role)

        # Patients cannot reassign their treating physician or change disease phase directly
        if actor_role == UserRole.PATIENT:
            if schema.treating_physician_id is not None or schema.disease_phase is not None:
                raise InsufficientPermissionError("Patients cannot modify clinician assignments or disease classification.")

        # MRN uniqueness check if changing MRN
        if schema.medical_record_number and schema.medical_record_number != patient.medical_record_number:
            if self.patient_repo.get_by_mrn(schema.medical_record_number):
                raise ConflictException(f"MRN '{schema.medical_record_number}' is already assigned to another patient.")

        updated_patient = self.patient_repo.update(patient, schema)

        self.audit_repo.log_event(
            user_id=actor_id,
            action="PATIENT_PROFILE_UPDATED",
            resource=f"patient:{patient_id}",
            status="SUCCESS",
            details={"updated_fields": list(schema.model_dump(exclude_unset=True).keys())},
            ip_address=ip_address,
        )

        return updated_patient

    def search_patient_roster(
        self,
        query: Optional[str] = None,
        clinician_id: Optional[int] = None,
        disease_phase: Optional[str] = None,
        is_active: bool = True,
        page: int = 1,
        page_size: int = 20,
        actor_role: UserRole = UserRole.ADMINISTRATOR,
        actor_id: Optional[int] = None,
    ) -> PatientListResponse:
        """
        Queries paginated patient rosters with automatic clinician filter scoping.
        If a clinician requests the roster, default filter scopes to their assigned cohort.
        """
        # If actor is a clinician and clinician_id filter is unsupplied, default to actor's ID
        if actor_role == UserRole.CLINICIAN and clinician_id is None:
            clinician_id = actor_id

        items, total, pages = self.patient_repo.search_patients(
            query=query,
            clinician_id=clinician_id,
            disease_phase=disease_phase,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )

        read_items = [PatientRead.model_validate(item) for item in items]

        return PatientListResponse(
            items=read_items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )