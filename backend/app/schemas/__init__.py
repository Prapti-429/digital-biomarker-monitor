"""
Application Schemas Package Initialization.

Exports all Pydantic v2 schemas across domain modules.
"""

from app.schemas.auth_enums import UserRole, Permission, TokenType
from app.schemas.auth_schemas import (
    UserRegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    ChangePasswordRequest,
)
from app.schemas.user_schemas import UserRead, UserProfileUpdate, UserAdminUpdate, UserListResponse
from app.schemas.audit_schemas import AuditLogRead, AuditLogListResponse
from app.schemas.patient_schemas import (
    PatientCreate,
    PatientUpdate,
    PatientRead,
    PatientListResponse,
)
from app.schemas.medication_schemas import (
    MedicationRegimenCreate,
    MedicationRegimenUpdate,
    MedicationRegimenRead,
    MedicationAdherenceLogCreate,
    MedicationAdherenceLogRead,
    MedicationRegimenListResponse,
)
from app.schemas.vitals_schemas import (
    VitalSignsCreate,
    VitalSignsRead,
    VitalSignsListResponse,
)
from app.schemas.labs_schemas import (
    LabResultCreate,
    LabResultUpdate,
    LabResultRead,
    LabResultListResponse,
)
from app.schemas.symptom_schemas import (
    SymptomLogCreate,
    SymptomLogRead,
    SymptomLogListResponse,
)
from app.schemas.lifestyle_schemas import (
    NutritionLogCreate,
    NutritionLogRead,
    NutritionLogListResponse,
    LifestyleLogCreate,
    LifestyleLogRead,
    LifestyleLogListResponse,
)

__all__ = [
    "UserRole",
    "Permission",
    "TokenType",
    "UserRegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "ChangePasswordRequest",
    "UserRead",
    "UserProfileUpdate",
    "UserAdminUpdate",
    "UserListResponse",
    "AuditLogRead",
    "AuditLogListResponse",
    "PatientCreate",
    "PatientUpdate",
    "PatientRead",
    "PatientListResponse",
    "MedicationRegimenCreate",
    "MedicationRegimenUpdate",
    "MedicationRegimenRead",
    "MedicationAdherenceLogCreate",
    "MedicationAdherenceLogRead",
    "MedicationRegimenListResponse",
    "VitalSignsCreate",
    "VitalSignsRead",
    "VitalSignsListResponse",
    "LabResultCreate",
    "LabResultUpdate",
    "LabResultRead",
    "LabResultListResponse",
    "SymptomLogCreate",
    "SymptomLogRead",
    "SymptomLogListResponse",
    "NutritionLogCreate",
    "NutritionLogRead",
    "NutritionLogListResponse",
    "LifestyleLogCreate",
    "LifestyleLogRead",
    "LifestyleLogListResponse",
]