"""
AI Result Repository handling biomarker evaluation outputs, inference metrics, and scoring.
"""

from typing import List, Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import AIResult, DailyCheckIn
from app.repositories.base import BaseRepository, RepositoryError


class AIResultRepository(BaseRepository[AIResult, Any, Any]):
    """
    Repository handling model outputs, extracted features, and risk scoring.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(AIResult, session)

    def save_ai_result(
        self, result_data: Dict[str, Any], auto_commit: bool = True
    ) -> AIResult:
        """
        Persist model evaluation score and biomarker feature payload.
        """
        return self.create(obj_in=result_data, auto_commit=auto_commit)

    def retrieve_ai_results(self, check_in_id: int) -> List[AIResult]:
        """
        Fetch model processing results generated for a single check-in session.
        """
        try:
            stmt = select(AIResult).where(AIResult.check_in_id == check_in_id)
            return list(self.session.execute(stmt).scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Error retrieving AI results for CheckIn {check_in_id}", e
            )

    def retrieve_latest_score(self, patient_id: int) -> Optional[AIResult]:
        """
        Get the most recent AI biomarker score calculated for a patient.
        """
        try:
            stmt = (
                select(AIResult)
                .join(DailyCheckIn, AIResult.check_in_id == DailyCheckIn.id)
                .where(DailyCheckIn.patient_id == patient_id)
                .order_by(AIResult.created_at.desc())
                .limit(1)
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Failed to retrieve latest AI score for Patient {patient_id}", e
            )

    def retrieve_historical_scores(self, patient_id: int) -> List[AIResult]:
        """
        Retrieve all historic biomarker score evaluations for trend modeling.
        """
        try:
            stmt = (
                select(AIResult)
                .join(DailyCheckIn, AIResult.check_in_id == DailyCheckIn.id)
                .where(DailyCheckIn.patient_id == patient_id)
                .order_by(AIResult.created_at.asc())
            )
            return list(self.session.execute(stmt).scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Error fetching historical AI score trend for Patient {patient_id}", e
            )