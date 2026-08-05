"""
Repository Layer Package Initialization.
Exports all entity repositories, base generic structures, pagination parameters,
and custom exceptions for the Digital Biomarker Monitor.
"""

from app.repositories.base import (
    BaseRepository,
    PaginatedResult,
    PaginationParams,
    SortOrder,
    SortParam,
    RepositoryError,
    EntityNotFoundError,
    DuplicateEntityError,
)
from app.repositories.user_repository import UserRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.checkin_repository import DailyCheckInRepository
from app.repositories.symptom_repository import SymptomRepository
from app.repositories.audio_repository import AudioRepository
from app.repositories.video_repository import VideoRepository
from app.repositories.ai_result_repository import AIResultRepository

__all__ = [
    "BaseRepository",
    "PaginatedResult",
    "PaginationParams",
    "SortOrder",
    "SortParam",
    "RepositoryError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "UserRepository",
    "PatientRepository",
    "DailyCheckInRepository",
    "SymptomRepository",
    "AudioRepository",
    "VideoRepository",
    "AIResultRepository",
]