"""Personalized multimodal digital-biomarker inference service.

Observational monitoring only: this service detects deviations from a user's
longitudinal baseline. It does not diagnose disease or make treatment decisions.
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
from app.schemas.ai_schemas import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    AIHistoryPoint,
    AIHistoryResponse,
    BiomarkerFeatureRead,
)

MODEL_NAME = "Nuvyra Personalized Multimodal Anomaly Model"
MODEL_VERSION = "1.1.0"
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
                select(BiomarkerFeature).where(BiomarkerFeature.check_in_id == check_in.id)
            ).scalars().all()
            output.append((check_in, score, {f.feature_name: float(f.feature_value) for f in feature_rows}))
        return output

    @staticmethod
    def _mad(values: List[float], center: float) -> float:
        return median([abs(v - center) for v in values]) if values else 0.0

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

                names = [name for name, _ in FEATURES if name in current and all(name in row for row in history_features)]
                if len(names) >= 4:
                    matrix = np.array([[row[name] for name in names] for row in history_features], dtype=float)
                    current_vector = np.array([[current[name] for name in names]], dtype=float)
                    model = IsolationForest(n_estimators=100, contamination="auto", random_state=42)
                    model.fit(matrix)
                    decision = float(model.decision_function(current_vector)[0])
                    anomaly = max(0.0, min(1.0, 0.5 - decision))
                    robust = max(0.0, min(1.0, (sum(min(d, 4.0) for d in deviations.values()) / max(len(deviations), 1)) / 4.0))
                    score = max(0.0, min(100.0, 100.0 * (1.0 - (0.70 * anomaly + 0.30 * robust))))
                    confidence = min(0.95, 0.55 + n * 0.015)
                    return score, "isolation_forest+robust_baseline", confidence, deviations
            except Exception:
                pass

        if not deviations:
            return 82.0, "robust_baseline_initialization", 0.45, deviations
        mean_deviation = sum(min(d, 4.0) for d in deviations.values()) / len(deviations)
        return max(0.0, min(100.0, 100.0 - mean_deviation * 18.0)), "robust_personal_baseline", min(0.85, 0.45 + n * 0.03), deviations

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
    def _modalities(current: Dict[str, float]) -> List[str]:
        return sorted({category for name, category in FEATURES if name in current})

    @staticmethod
    def _quality(current: Dict[str, float], payload: AIAnalysisRequest) -> float:
        available = len(current) / len(FEATURES)
        duration = min(1.0, payload.source_duration_seconds / 10.0) if payload.source_duration_seconds else 0.0
        return round(min(1.0, 0.75 * available + 0.25 * duration), 3)

    @staticmethod
    def _drivers(deviations: Dict[str, float]) -> List[str]:
        return [name.replace("_", " ") for name, value in sorted(deviations.items(), key=lambda item: item[1], reverse=True)[:3] if value >= 1.0]

    @staticmethod
    def _recommendations(score: float, trend: str, quality: float) -> List[str]:
        recommendations = [
            "Keep measurement conditions as consistent as practical so the personal baseline remains comparable.",
            "Review the longitudinal trend rather than interpreting a single observation in isolation.",
        ]
        if quality < 0.6:
            recommendations.append("Consider completing more available signal groups on the next check-in to improve data quality.")
        if trend == "DEGRADING" or score < 60:
            recommendations.append("If changes persist or concern you, discuss them with a qualified healthcare professional.")
        return recommendations

    @staticmethod
    def _limitations(history_count: int, current: Dict[str, float]) -> List[str]:
        limitations = [
            "This is an observational digital-biomarker model, not a diagnostic or treatment system.",
            "Results can be affected by device, environment, recording quality and day-to-day variation.",
        ]
        if history_count < 5:
            limitations.append("The personal baseline is still developing; confidence should increase with repeated observations.")
        if not any(name.startswith("voice_") for name in current):
            limitations.append("No acoustic features were supplied for this observation.")
        if not any(name.startswith("face_") for name in current):
            limitations.append("No facial-motion features were supplied for this observation.")
        return limitations

    @staticmethod
    def _explanation(score: float, trend: str, deviations: Dict[str, float]) -> str:
        notable = [name.replace("_", " ") for name, value in sorted(deviations.items(), key=lambda item: item[1], reverse=True)[:3] if value >= 1.0]
        labels = ", ".join(notable) if notable else "the available signals"
        if score >= 80:
            state = "The current session is broadly consistent with the personal baseline."
        elif score >= 60:
            state = "The current session shows moderate deviation from the personal baseline."
        else:
            state = "The current session shows substantial deviation from the personal baseline."
        return f"{state} The largest observed deviations were in {labels}. Trend classification: {trend}. This is an observational signal, not a medical diagnosis."

    def analyze(self, user_id: UUID, payload: AIAnalysisRequest) -> AIAnalysisResponse:
        current = self._vector(payload)
        history = self._history(user_id)
        history_features = [row[2] for row in history]
        score, algorithm, confidence, deviations = self._model_score(current, history_features)
        previous_score = history[0][1].overall_score if history else None
        trend = self._trend(score, previous_score)
        now = datetime.now(timezone.utc)
        quality = self._quality(current, payload)
        modalities = self._modalities(current)
        drivers = self._drivers(deviations)
        recommendations = self._recommendations(score, trend, quality)
        limitations = self._limitations(len(history_features), current)

        check_in = DailyCheckIn(user_id=user_id, check_in_date=date.today(), status="completed", completed_at=now, extra_metadata={"source": "web_check_in", "model_version": MODEL_VERSION})
        self.db.add(check_in)
        self.db.flush()

        feature_reads: List[BiomarkerFeatureRead] = []
        for name, category in FEATURES:
            if name not in current:
                continue
            value = current[name]
            self.db.add(BiomarkerFeature(check_in_id=check_in.id, feature_name=name, feature_category=category, feature_value=value, source_modality=category, extracted_at=now, extra_properties={"model_version": MODEL_VERSION}))
            feature_reads.append(BiomarkerFeatureRead(name=name, category=category, value=value, deviation=deviations.get(name)))

        explanation = self._explanation(score, trend, deviations)
        self.db.add(HealthStabilityScore(
            check_in_id=check_in.id,
            overall_score=round(score, 2),
            trend_category=trend,
            confidence=round(confidence, 3),
            generated_at=now,
            explanation_summary=explanation,
            model_metadata={
                "model_name": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "algorithm": algorithm,
                "baseline_observations": len(history_features),
                "data_quality_score": quality,
                "modalities_present": modalities,
                "top_drivers": drivers,
                "recommendations": recommendations,
                "limitations": limitations,
                "source_duration_seconds": payload.source_duration_seconds,
            },
        ))
        self.db.commit()

        return AIAnalysisResponse(check_in_id=check_in.id, overall_score=round(score, 2), trend=trend, confidence=round(confidence, 3), model_name=MODEL_NAME, model_version=MODEL_VERSION, baseline_observations=len(history_features), explanation=explanation, features=feature_reads, generated_at=now, data_quality_score=quality, modalities_present=modalities, top_drivers=drivers, recommendations=recommendations, limitations=limitations)

    def history(self, user_id: UUID, limit: int = 30) -> AIHistoryResponse:
        rows = self._history(user_id, limit=limit)
        return AIHistoryResponse(
            items=[AIHistoryPoint(check_in_id=check_in.id, score=round(score.overall_score, 2), trend=score.trend_category, confidence=round(score.confidence, 3), generated_at=score.generated_at) for check_in, score, _ in reversed(rows)],
            baseline_observations=len(rows), model_name=MODEL_NAME, model_version=MODEL_VERSION,
        )

    def latest(self, user_id: UUID) -> Optional[AIAnalysisResponse]:
        rows = self._history(user_id, limit=1)
        if not rows:
            return None
        check_in, score, _ = rows[0]
        feature_rows = self.db.execute(select(BiomarkerFeature).where(BiomarkerFeature.check_in_id == check_in.id)).scalars().all()
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
            features=[BiomarkerFeatureRead(name=f.feature_name, category=f.feature_category, value=float(f.feature_value), deviation=None) for f in feature_rows],
            generated_at=score.generated_at,
            data_quality_score=float(metadata.get("data_quality_score", 0)),
            modalities_present=list(metadata.get("modalities_present", [])),
            top_drivers=list(metadata.get("top_drivers", [])),
            recommendations=list(metadata.get("recommendations", [])),
            limitations=list(metadata.get("limitations", [])),
        )
