"""
Symptom Repository for managing logged symptom instances and analytical trend queries.
"""

from typing import List, Any, Dict, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import Symptom, DailyCheckIn
from app.repositories.base import BaseRepository, RepositoryError


class SymptomRepository(BaseRepository[Symptom, Any, Any]):
    """
    Repository class handling symptom monitoring metrics and severity tracking.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(Symptom, session)

    def create_symptom(self, symptom_data: Dict[str, Any], auto_commit: bool = True) -> Symptom:
        """
        Attach a logged symptom entry to a check-in session.
        """
        return self.create(obj_in=symptom_data, auto_commit=auto_commit)

    def get_symptom_trends(
        self,
        patient_id: int,
        symptom_name: str,
        start_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract severity trends over time for a specific named symptom.
        """
        try:
            stmt = (
                select(Symptom.severity_score, DailyCheckIn.check_in_date)
                .join(DailyCheckIn, Symptom.check_in_id == DailyCheckIn.id)
                .where(
                    and_(
                        DailyCheckIn.patient_id == patient_id,
                        Symptom.symptom_name.ilike(f"%{symptom_name}%"),
                    )
                )
            )

            if start_date:
                stmt = stmt.where(DailyCheckIn.check_in_date >= start_date)

            stmt = stmt.order_by(DailyCheckIn.check_in_date.asc())
            results = self.session.execute(stmt).all()

            return [
                {"severity": row.severity_score, "timestamp": row.check_in_date}
                for row in results
            ]
        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Error calculating symptom trends for Patient {patient_id}", e
            )

    def get_historical_symptoms(self, check_in_ids: List[int]) -> List[Symptom]:
        """
        Fetch all symptoms recorded across a set of check-in IDs.
        """
        try:
            stmt = select(Symptom).where(Symptom.check_in_id.in_(check_in_ids))
            return list(self.session.execute(stmt).scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError("Error executing historical symptom query", e)