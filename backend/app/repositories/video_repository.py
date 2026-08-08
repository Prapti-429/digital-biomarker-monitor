"""
Video Record Repository managing facial video files, spatial metrics, and timelines.
"""

from typing import List, Any, Dict
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.video_recording import VideoRecording
from app.db.models.daily_check_in import DailyCheckIn
from app.repositories.base import BaseRepository, RepositoryError


class VideoRepository(BaseRepository[VideoRecord, Any, Any]):
    """
    Repository class managing facial and gait video biomarker entries.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(VideoRecord, session)

    def create_video_record(
        self, video_data: Dict[str, Any], auto_commit: bool = True
    ) -> VideoRecord:
        """
        Save reference metadata for a video stream upload.
        """
        return self.create(obj_in=video_data, auto_commit=auto_commit)

    def update_metadata(self, video_id: int, metadata: Dict[str, Any]) -> VideoRecord:
        """
        Update resolution, frame rates, or duration for a video entry.
        """
        return self.update(id_val=video_id, obj_in=metadata, auto_commit=True)

    def retrieve_video_timeline(self, patient_id: int) -> List[VideoRecord]:
        """
        Fetch video assets across time for a patient's longitudinal analysis.
        """
        try:
            stmt = (
                select(VideoRecord)
                .join(DailyCheckIn, VideoRecord.check_in_id == DailyCheckIn.id)
                .where(DailyCheckIn.patient_id == patient_id)
                .order_by(VideoRecord.created_at.asc())
            )
            return list(self.session.execute(stmt).scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Failed to retrieve video timeline for Patient {patient_id}", e
            )