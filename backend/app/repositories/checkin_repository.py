"""
Daily Check-in Repository managing patient check-in entries and multi-modal attachments.
"""

from typing import Optional, List, Any, Dict
from datetime import datetime, time, timedelta
from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.models import DailyCheckIn
from app.repositories.base import BaseRepository, EntityNotFoundError, RepositoryError


class DailyCheckInRepository(BaseRepository[DailyCheckIn, Any, Any]):
    """
    Repository class handling daily patient log check-ins.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(DailyCheckIn, session)

    def create_checkin(self, checkin_data: Dict[str, Any], auto_commit: bool = True) -> DailyCheckIn:
        """
        Register a new daily check-in.
        """
        return self.create(obj_in=checkin_data, auto_commit=auto_commit)

    def get_todays_checkin(self, patient_id: int) -> Optional[DailyCheckIn]:
        """
        Check if a patient has completed a check-in today.
        """
        try:
            today_start = datetime.combine(datetime.utcnow().date(), time.min)
            today_end = datetime.combine(datetime.utcnow().date(), time.max)

            stmt = (
                select(DailyCheckIn)
                .where(
                    and_(
                        DailyCheckIn.patient_id == patient_id,
                        DailyCheckIn.check_in_date >= today_start,
                        DailyCheckIn.check_in_date <= today_end,
                    )
                )
                .options(
                    selectinload(DailyCheckIn.symptoms),
                    selectinload(DailyCheckIn.audio_records),
                    selectinload(DailyCheckIn.video_records),
                    selectinload(DailyCheckIn.ai_results),
                )
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to fetch today's check-in for Patient {patient_id}", e)

    def get_last_30_days(self, patient_id: int) -> List[DailyCheckIn]:
        """
        Fetch check-in logs over the past 30-day window.
        """
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        return self.get_date_range(patient_id=patient_id, start_date=thirty_days_ago)

    def get_date_range(
        self,
        patient_id: int,
        start_date: datetime,
        end_date: Optional[datetime] = None,
    ) -> List[DailyCheckIn]:
        """
        Query check-in logs within explicit datetime bounds.
        """
        try:
            end_val = end_date or datetime.utcnow()
            stmt = (
                select(DailyCheckIn)
                .where(
                    and_(
                        DailyCheckIn.patient_id == patient_id,
                        DailyCheckIn.check_in_date >= start_date,
                        DailyCheckIn.check_in_date <= end_val,
                    )
                )
                .options(
                    selectinload(DailyCheckIn.symptoms),
                    selectinload(DailyCheckIn.ai_results),
                )
                .order_by(DailyCheckIn.check_in_date.desc())
            )
            results = self.session.execute(stmt).scalars().all()
            return list(results)
        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Error fetching date range check-ins for Patient {patient_id}", e
            )