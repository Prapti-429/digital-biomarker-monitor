"""
Audio Record Repository managing audio files and biomarker processing states.
"""

from typing import List, Any, Dict, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.audio_recording import AudioRecording
from app.db.models.daily_check_in import DailyCheckIn
from app.repositories.base import BaseRepository, RepositoryError


class AudioRepository(BaseRepository[AudioRecord, Any, Any]):
    """
    Repository class handling audio media file recordings.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(AudioRecord, session)

    def create_audio_record(
        self, audio_data: Dict[str, Any], auto_commit: bool = True
    ) -> AudioRecord:
        """
        Persist a new audio recording reference.
        """
        return self.create(obj_in=audio_data, auto_commit=auto_commit)

    def update_processing_status(
        self, audio_id: int, status: str, details: Optional[Dict[str, Any]] = None
    ) -> AudioRecord:
        """
        Update the downstream processing state of an audio file.
        """
        try:
            record = self.get_by_id(audio_id)
            if hasattr(record, "status"):
                setattr(record, "status", status)
            if details and hasattr(record, "processing_metadata"):
                setattr(record, "processing_metadata", details)

            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
            return record
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError(
                f"Failed to update processing status for Audio record {audio_id}", e
            )

    def get_audio_history(self, patient_id: int) -> List[AudioRecord]:
        """
        Retrieve all audio recordings associated with a given patient.
        """
        try:
            stmt = (
                select(AudioRecord)
                .join(DailyCheckIn, AudioRecord.check_in_id == DailyCheckIn.id)
                .where(DailyCheckIn.patient_id == patient_id)
                .order_by(AudioRecord.created_at.desc())
            )
            return list(self.session.execute(stmt).scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Failed to retrieve audio history for Patient {patient_id}", e
            )