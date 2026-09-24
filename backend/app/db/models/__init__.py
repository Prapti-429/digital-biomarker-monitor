from app.db.models.patient import PatientProfile
from app.db.models.user import User
from app.db.models.audio_recording import AudioRecording
from app.db.models.video_recording import VideoRecording
from app.db.models.biomarker_feature import BiomarkerFeature
from app.db.models.daily_check_in import DailyCheckIn
from app.db.models.health_stability_score import HealthStabilityScore
from app.db.models.symptom_report import SymptomReport
from app.db.models.medication import MedicationRegimen, MedicationAdherenceLog
from app.db.models.vitals import VitalSigns
from app.db.models.labs import LabResult
from app.db.models.symptoms import SymptomLog
from app.db.models.lifestyle import NutritionLog, LifestyleLog
from app.db.models.file_upload import FileUploadRecord
from app.db.models.past_history import PastHistoryRecord, MedicalDocument, HealthReminder

# Authentication/session and audit models must be imported into Base.metadata.
# Without these imports, Alembic's bootstrap create_all() cannot discover the
# session, refresh-token, RBAC, password-reset, email-verification, and audit
# tables required by the production login flow.
from app.db.models.auth_models import (
    Role,
    Permission,
    UserSession,
    RefreshToken,
    PasswordResetToken,
    EmailVerificationToken,
)
from app.db.models.audit_models import AuditLog

__all__ = [
    "User", "PatientProfile", "AudioRecording", "VideoRecording", "BiomarkerFeature",
    "DailyCheckIn", "HealthStabilityScore", "SymptomReport", "MedicationRegimen",
    "MedicationAdherenceLog", "VitalSigns", "LabResult", "SymptomLog", "NutritionLog",
    "LifestyleLog", "FileUploadRecord", "PastHistoryRecord", "MedicalDocument", "HealthReminder",
    "Role", "Permission", "UserSession", "RefreshToken", "PasswordResetToken",
    "EmailVerificationToken", "AuditLog",
]
