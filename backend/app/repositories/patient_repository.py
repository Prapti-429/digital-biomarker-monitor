"""
Patient Repository handling medical profile queries and longitudinal histories.
"""

from typing import Optional, List, Any, Dict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.models import Patient, DailyCheckIn
from app.repositories.base import BaseRepository, EntityNotFoundError, RepositoryError


class PatientRepository(BaseRepository[Patient, Any, Any]):
    """
    Repository layer for Patient clinical profile management.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(Patient, session)

    def create_patient(self, patient_data: Dict[str, Any], auto_commit: bool = True) -> Patient:
        """
        Create a patient profile linked to a User record.
        """
        return self.create(obj_in=patient_data, auto_commit=auto_commit)

    def get_by_user_id(self, user_id: int) -> Optional[Patient]:
        """
        Fetch patient profile associated with a specific User ID.
        """
        try:
            stmt = select(Patient).where(Patient.user_id == user_id)
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching patient for User ID {user_id}", e)

    def get_patient_with_checkins(self, patient_id: int) -> Patient:
        """
        Fetch a patient eagerly loading all historic check-ins.
        """
        try:
            stmt = (
                select(Patient)
                .where(Patient.id == patient_id)
                .options(selectinload(Patient.check_ins))
            )
            patient = self.session.execute(stmt).scalar_one_or_none()
            if not patient:
                raise EntityNotFoundError("Patient", patient_id)
            return patient
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to retrieve patient check-ins for ID {patient_id}", e)

    def get_longitudinal_history(
        self,
        patient_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[DailyCheckIn]:
        """
        Retrieve chronological daily check-in records for longitudinal analysis.
        """
        try:
            stmt = (
                select(DailyCheckIn)
                .where(DailyCheckIn.patient_id == patient_id)
                .options(
                    selectinload(DailyCheckIn.symptoms),
                    selectinload(DailyCheckIn.ai_results),
                    selectinload(DailyCheckIn.audio_records),
                    selectinload(DailyCheckIn.video_records),
                )
            )

            if start_date:
                stmt = stmt.where(DailyCheckIn.check_in_date >= start_date)
            if end_date:
                stmt = stmt.where(DailyCheckIn.check_in_date <= end_date)

            stmt = stmt.order_by(DailyCheckIn.check_in_date.asc())
            results = self.session.execute(stmt).scalars().all()
            return list(results)
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error fetching longitudinal history for Patient {patient_id}", e)