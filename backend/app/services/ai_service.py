"""Personalized multimodal digital-biomarker inference service.

This is an observational monitoring model, not a diagnostic model. It learns each
user's longitudinal baseline and flags deviations from that baseline. When enough
history exists, Isolation Forest is used as the anomaly-learning component; with
short histories, a robust median/MAD deviation model is used so the first sessions
remain useful and deterministic.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from math import isfinite
from statistics import median
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.biomarker_feature import BiomarkerFeature
from app.db.models.daily_check_in import DailyCheckIn
from app.db.models.health_stability_score import HealthStabilityScore
from app.schemas.ai_schemas import AIAnalysisRequest, AIAnalysisResponse, AIHistoryPoint, AIHistoryResponse, BiomarkerFeatureRead

MODEL_NAME = "Nuvyra Personalized Multimodal Anomaly Model"
MODEL_VERSION = "1.0.0"
FEATURES = (
    ("fatigue", "survey"),
    ("mood_deviation", "survey"),
    ("symptom_burden", "survey"),
    ("voice_rms", "acoustic"),
    ("voice_zero_crossing_rate", "acoustic"),
    ("voice_pitch_hz", "acoustic"),
    ("voice_speech_activity", "acoustic"),
    ("face_motion", "facial_motion"),
    ("face_luminance_variability", "facial_motion"),
    ("face_blink_proxy", "facial_motion"),
)


class AIService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _safe(value: Optional[float]) -> Optional[float]:
        if value is None or not isfinite(float(value)):
            return None
        return float(value)

    def _vector(self, payload: AIAnalysisRequest) -> Dict[str, float]:
        values = payload.model_dump()
        result: Dict[str, float] = {}
        for name, _category in FEATURES:
            value = self._safe(values.get(name))
            if value is not None:
                result[name] = value
        return result

    def _history(self, user_id: UUID, limit: int = 30) -> List[Tuple[DailyCheckIn, HealthStabilityScore, Dict[str, float]]]:
        rows = self.db.execute(
            select(DailyCheckIn, HealthStabilityScore)
            .join(HealthStabilityScore, HealthStabilityScore.check_in_id == DailyCheckIn.id)
            .where(DailyCheckIn.user_id == user_id)
            .order_by(HealthStabilityScore.generated_at.desc())
            .limit(limit)
        ).all()
        output = []
        for check_in, score in rows:
            feature_rows = self.db.execute(
                select(BiomarkerFeature)
                .where(BiomarkerFeature.check_in_id == check_in.id)
            ).scalars().all()
            features = {f.feature_name: float(f.feature_value) for f in feature_rows}
            output.append((check_in, score, features))
        return output

    @staticmethod
    def _mad(values: List[float], center: float) -> float:
        deviations = [abs(v - center) for v in values]
        return median(deviations) if deviations else 0.0

    def _robust_deviations(self, current: Dict[str, float], history_features: List[Dict[str, float]]) -> Dict[str, float]:
        deviations: Dict[str, float] = {}
        for name, value in current.items():
            baseline = [row[name] for row in history_features if name in row]
            if not baseline:
                continue
            center = median(baseline)
            mad = self._mad(baseline, center)
            scale = max(1.4826 * mad, abs(center) * 0.05, 0.01)
            deviations[name] = abs(value - center) / scale
        return deviations

    def _model_score(self, current: Dict[str, float], history_features: List[Dict[str, float]]) -> Tuple[float, str, float, Dict[str, float]]:
        deviations = self._robust_deviations(current, history_features)
        n = len(history_features)

        if n >= 5 and len(current) >= 4:
            try:
                from sklearn.ensemble import IsolationForest
                import numpy as np

                names = [name for name, _category in FEATURES if name in current and all(name in row for row in history_features)]
                if len(names) >= 4:
                    matrix = np.array([[row[name] for name in names] for row in history_features], dtype=float)
                    current_vector = np.array([[current[name] for name in names]], dtype=float)
                    model = IsolationForest(
                        n_estimators=100,
                        contamination="auto",
                        random_state=42,
                    )
                    model.fit(matrix)
                    decision = float(model.decision_function(current_vector)[0])
                    anomaly = max(0.0, min(1.0, 0.5 - decision))
                    robust = max(0.0, min(1.0, (sum(min(d, 4.0) for d in deviations.values()) / max(len(deviations), 1)) / 4.0))
                    score = max(0.0, min(100.0, 100.0 * (1.0 - (0.70 * anomaly + 0.30 * robust))))
                    confidence = min(0.95, 0.55 + n * 0.015)
                    return score, "isolation_forest+robust_baseline", confidence, deviations
            except Exception:
                # Fall through to the deterministic baseline model if ML dependencies
                # are unavailable or a sparse feature matrix cannot be fitted.
                pass

        if not deviations:
            return 82.0, "robust_baseline_initialization", 0.45, deviations
        mean_deviation = sum(min(d, 4.0) for d in deviations.values()) / len(deviations)
        score = max(0.0, min(100.0, 100.0 - mean_deviation * 18.0))
        confidence = min(0.85, 0.45 + n * 0.03)
        return score, "robust_personal_baseline", confidence, deviations

    @staticmethod
    def _trend(score: float, previous: Optional[float]) -> str:
        if previous is None:
            return "INITIAL"
        delta = score - previous
        if delta >= 3:
            return "IMPROVING"
        if delta <= -3:
            return "DEGRADING"
        return "STABLE"

    @staticmethod
    def _explanation(score: float, trend: str, deviations: Dict[str, float]) -> str:
        notable = sorted(deviations.items(), key=lambda item: item[1], reverse=True)[:3]
        if notable:
            labels = ", ".join(name.replace("_", " ") for name, value in notable if value >= 1.0)
        else:
            labels = "the available signals"
        if score >= 80:
            state = "The current session is broadly consistent with the personal baseline."
        elif score >= 60:
            state = "The current session shows moderate deviation from the personal baseline."
        else:
            state = "The current session shows substantial deviation from the personal baseline."
        return f"{state} The model observed the largest deviations in {labels}. Trend classification: {trend}. This score is an observational signal and is not a medical diagnosis."

    def analyze(self, user_id: UUID, payload: AIAnalysisRequest) -> AIAnalysisResponse:
        current = self._vector(payload)
        history = self._history(user_id)
        history_features = [row[2] for row in history]
        score, model_name, confidence, deviations = self._model_score(current, history_features)
        previous_score = history[0][1].overall_score if history else None
        trend = self._trend(score, previous_score)
        now = datetime.now(timezone.utc)

        check_in = DailyCheckIn(
            user_id=user_id,
            check_in_date=date.today(),
            status="completed",
            completed_at=now,
            extra_metadata={"source": "web_check_in", "model_version": MODEL_VERSION},
        )
        self.db.add(check_in)
        self.db.flush()

        feature_reads: List[BiomarkerFeatureRead] = []
        for name, category in FEATURES:
            if name not in current:
                continue
            value = current[name]
            feature = BiomarkerFeature(
                check_in_id=check_in.id,
                feature_name=name,
                feature_category=category,
                feature_value=value,
                source_modality=category,
                extracted_at=now,
                extra_properties={"model_version": MODEL_VERSION},
            )
            self.db.add(feature)
            feature_reads.append(BiomarkerFeatureRead(name=name, category=category, value=value, deviation=deviations.get(name)))

        stability = HealthStabilityScore(
            check_in_id=check_in.id,
            overall_score=round(score, 2),
            trend_category=trend,
            confidence=round(confidence, 3),
            generated_at=now,
            explanation_summary=self._explanation(score, trend, deviations),
            model_metadata={
                "model_name": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "algorithm": model_name,
                "baseline_observations": len(history_features),
                "source_duration_seconds": payload.source_duration_seconds,
            },
        )
        self.db.add(stability)
        self.db.commit()

        return AIAnalysisResponse(
            check_in_id=check_in.id,
            overall_score=round(score, 2),
            trend=trend,
            confidence=round(confidence, 3),
            model_name=MODEL_NAME,
            model_version=MODEL_VERSION,
            baseline_observations=len(history_features),
            explanation=self._explanation(score, trend, deviations),
            features=feature_reads,
            generated_at=now,
        )

    def history(self, user_id: UUID, limit: int = 30) -> AIHistoryResponse:
        rows = self._history(user_id, limit=limit)
        items = [
            AIHistoryPoint(
                check_in_id=check_in.id,
                score=round(score.overall_score, 2),
                trend=score.trend_category,
                confidence=round(score.confidence, 3),
                generated_at=score.generated_at,
            )
            for check_in, score, _features in reversed(rows)
        ]
        return AIHistoryResponse(
            items=items,
            baseline_observations=len(rows),
            model_name=MODEL_NAME,
            model_version=MODEL_VERSION,
        )

    def latest(self, user_id: UUID) -> Optional[AIAnalysisResponse]:
        history = self._history(user_id, limit=1)
        if not history:
            return None
        check_in, score, feature_values = history[0]
        feature_rows = self.db.execute(
            select(BiomarkerFeature).where(BiomarkerFeature.check_in_id == check_in.id)
        ).scalars().all()
        features = [
            BiomarkerFeatureRead(
                name=f.feature_name,
                category=f.feature_category,
                value=float(f.feature_value),
                deviation=None,
            )
            for f in feature_rows
        ]
        metadata = score.model_metadata or {}
        return AIAnalysisResponse(
            check_in_id=check_in.id,
            overall_score=round(score.overall_score, 2),
            trend=score.trend_category,
            confidence=round(score.confidence, 3),
            model_name=str(metadata.get("model_name", MODEL_NAME)),
            model_version=str(metadata.get("model_version", MODEL_VERSION)),
            baseline_observations=int(metadata.get("baseline_observations", 0)),
            explanation=score.explanation_summary or "No explanation available.",
            features=features,
            generated_at=score.generated_at,
        )
