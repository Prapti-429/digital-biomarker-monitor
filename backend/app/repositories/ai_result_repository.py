"""
Health Stability Score Repository.

Handles persistence and retrieval of aggregated AI inference results
and longitudinal health stability scores.
"""

from typing import List, Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.health_stability_score import HealthStabilityScore
from app.db.models.daily_check_in import DailyCheckIn
from app.repositories.base import BaseRepository, RepositoryError


class AIResultRepository(
    BaseRepository[HealthStabilityScore, Any, Any]
):
    """
    Repository for aggregated AI health-stability assessments.

    The repository name is retained for compatibility with the existing
    service/API layer, while the underlying ORM entity is
    HealthStabilityScore.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(HealthStabilityScore, session)

    def save_ai_result(
        self,
        result_data: Dict[str, Any],
        auto_commit: bool = True,
    ) -> HealthStabilityScore:
        """
        Persist an aggregated AI health-stability assessment.
        """
        return self.create(
            obj_in=result_data,
            auto_commit=auto_commit,
        )

    def retrieve_ai_results(
        self,
        check_in_id: int,
    ) -> List[HealthStabilityScore]:
        """
        Fetch the AI health-stability result for a check-in.

        HealthStabilityScore currently has a unique check_in_id,
        so this normally returns zero or one record.
        """
        try:
            stmt = select(HealthStabilityScore).where(
                HealthStabilityScore.check_in_id == check_in_id
            )

            return list(
                self.session.execute(stmt).scalars().all()
            )

        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Error retrieving AI result for CheckIn {check_in_id}",
                e,
            )

    def retrieve_latest_score(
        self,
        patient_id: int,
    ) -> Optional[HealthStabilityScore]:
        """
        Get the most recent health stability score for a patient.
        """
        try:
            stmt = (
                select(HealthStabilityScore)
                .join(
                    DailyCheckIn,
                    HealthStabilityScore.check_in_id
                    == DailyCheckIn.id,
                )
                .where(
                    DailyCheckIn.patient_id == patient_id
                )
                .order_by(
                    HealthStabilityScore.generated_at.desc()
                )
                .limit(1)
            )

            return self.session.execute(
                stmt
            ).scalar_one_or_none()

        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Failed to retrieve latest AI score "
                f"for Patient {patient_id}",
                e,
            )

    def retrieve_historical_scores(
        self,
        patient_id: int,
    ) -> List[HealthStabilityScore]:
        """
        Retrieve historical health stability scores for
        longitudinal trend analysis.
        """
        try:
            stmt = (
                select(HealthStabilityScore)
                .join(
                    DailyCheckIn,
                    HealthStabilityScore.check_in_id
                    == DailyCheckIn.id,
                )
                .where(
                    DailyCheckIn.patient_id == patient_id
                )
                .order_by(
                    HealthStabilityScore.generated_at.asc()
                )
            )

            return list(
                self.session.execute(stmt).scalars().all()
            )

        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Error fetching historical AI score trend "
                f"for Patient {patient_id}",
                e,
            )