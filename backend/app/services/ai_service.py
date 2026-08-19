"""Longitudinal multimodal digital-biomarker inference service.

Observational monitoring only. It detects change from an individual's own
baseline and uses user-provided history/document metadata as contextual
information; it does not diagnose disease or make treatment decisions.
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
from app.db.models.past_history import HealthReminder, MedicalDocument, PastHistoryRecord
from app.schemas.ai_schemas import AIAnalysisRequest, AIAnalysisResponse, AIHistoryPoint, AIHistoryResponse, AIContextSummary, BiomarkerFeatureRead

MODEL_NAME = "Nuvyra Multimodal Longitudinal Biomarker Engine"
MODEL_VERSION = "2.1.0"
FEATURES = (
    ("fatigue", "survey"), ("mood_deviation", "survey"), ("symptom_burden", "survey"),
    ("voice_rms", "voice"), ("voice_zero_crossing_rate", "voice"), ("voice_pitch_hz", "voice"),
    ("voice_speech_activity", "voice"), ("voice_speech_rate", "voice"), ("voice_pause_ratio", "voice"),
    ("face_motion", "facial_dynamics"), ("face_luminance_variability", "facial_dynamics"),
    ("face_blink_proxy", "eye"), ("blink_rate_per_minute", "eye"), ("eye_opening_proxy", "eye"),
    ("gait_motion", "gait_movement"), ("gait_variability", "gait_movement"),
    ("gait_symmetry_proxy", "gait_movement"), ("breathing_rate_per_minute", "breathing"),
    ("breathing_variability", "breathing"), ("head_motion", "head_movement"),
    ("head_motion_variability", "head_movement"),
)
MODALITY_NAMES = ["survey", "voice", "facial_dynamics", "eye", "gait_movement", "breathing", "head_movement"]


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
        return {name: value for name, _ in FEATURES if (value := self._safe(values.get(name))) is not None}

    def _history(self, user_id: UUID, limit: int = 30):
        rows = self.db.execute(
            select(DailyCheckIn, HealthStabilityScore)
            .join(HealthStabilityScore, HealthStabilityScore.check_in_id == DailyCheckIn.id)
            .where(DailyCheckIn.user_id == user_id)
            .order_by(HealthStabilityScore.generated_at.desc()).limit(limit)
        ).all()
        output = []
        for check_in, score in rows:
            feature_rows = self.db.execute(select(BiomarkerFeature).where(BiomarkerFeature.check_in_id == check_in.id)).scalars().all()
            output.append((check_in, score, {f.feature_name: float(f.feature_value) for f in feature_rows}))
        return output

    def _context(self, user_id: UUID) -> AIContextSummary:
        history_count = self.db.scalar(select(PastHistoryRecord).where(PastHistoryRecord.user_id == user_id).count()) if False else None
        history_rows = self.db.execute(select(PastHistoryRecord).where(PastHistoryRecord.user_id == user_id)).scalars().all()
        documents = self.db.execute(select(MedicalDocument).where(MedicalDocument.user_id == user_id)).scalars().all()
        pending = self.db.execute(select(HealthReminder).where(HealthReminder.user_id == user_id, HealthReminder.completed.is_(False))).scalars().all()
        types = sorted({d.document_type for d in documents if d.document_type})
        used = []
        if history_rows: used.append("user-reported past history")
        if documents: used.append("uploaded document metadata and extracted text availability")
        if pending: used.append("pending health reminders")
        return AIContextSummary(past_history_count=len(history_rows), document_count=len(documents), pending_reminder_count=len(pending), document_types=types, context_used=used)

    @staticmethod
    def _mad(values: List[float], center: float) -> float:
        return median([abs(v - center) for v in values]) if values else 0.0

    def _robust_deviations(self, current: Dict[str, float], history_features: List[Dict[str, float]]) -> Dict[str, float]:
        deviations = {}
        for name, value in current.items():
            baseline = [row[name] for row in history_features if name in row]
            if baseline:
                center = median(baseline)
                scale = max(1.4826 * self._mad(baseline, center), abs(center) * 0.05, 0.01)
                deviations[name] = abs(value - center) / scale
        return deviations

    def _model_score(self, current: Dict[str, float], history_features: List[Dict[str, float]]):
        deviations = self._robust_deviations(current, history_features)
        n = len(history_features)
        if n >= 5 and len(current) >= 4:
            try:
                from sklearn.ensemble import IsolationForest
                import numpy as np
                names = [name for name, _ in FEATURES if name in current and all(name in row for row in history_features)]
                if len(names) >= 4:
                    matrix = np.array([[row[name] for name in names] for row in history_features], dtype=float)
                    model = IsolationForest(n_estimators=150, contamination="auto", random_state=42)
                    model.fit(matrix)
                    decision = float(model.decision_function(np.array([[current[name] for name in names]], dtype=float))[0])
                    anomaly = max(0.0, min(1.0, 0.5 - decision))
                    robust = max(0.0, min(1.0, sum(min(d, 4) for d in deviations.values()) / max(len(deviations), 1) / 4))
                    score = 100 * (1 - (0.7 * anomaly + 0.3 * robust))
                    return max(0, min(100, score)), "isolation_forest+robust_baseline", min(0.95, 0.55 + n * 0.015), deviations
            except Exception:
                pass
        if not deviations:
            return 82.0, "robust_baseline_initialization", 0.45, deviations
        mean_dev = sum(min(d, 4) for d in deviations.values()) / len(deviations)
        return max(0, min(100, 100 - mean_dev * 18)), "robust_personal_baseline", min(0.9, 0.45 + n * 0.03), deviations

    @staticmethod
    def _trend(score: float, previous: Optional[float]) -> str:
        if previous is None: return "INITIAL"
        if score >= previous + 3: return "IMPROVING"
        if score <= previous - 3: return "DEGRADING"
        return "STABLE"

    @staticmethod
    def _modalities(current: Dict[str, float]) -> List[str]:
        return sorted({category for name, category in FEATURES if name in current})

    @staticmethod
    def _quality(current: Dict[str, float], payload: AIAnalysisRequest) -> float:
        available = len(current) / len(FEATURES)
        duration = min(1, payload.source_duration_seconds / 10) if payload.source_duration_seconds else 0
        return round(min(1, 0.75 * available + 0.25 * duration), 3)

    @staticmethod
    def _persistence(deviations: Dict[str, float], history: List[Tuple]) -> str:
        if len(history) < 3: return "INSUFFICIENT_HISTORY"
        notable = {k for k, v in deviations.items() if v >= 1.0}
        if not notable: return "NO_PERSISTENT_DEVIATION"
        recent = history[:3]
        return "PERSISTENT_CHANGE" if all(name in row[2] for name in notable for row in recent) else "SINGLE_SESSION_CHANGE"

    @staticmethod
    def _drivers(deviations):
        return [name.replace("_", " ") for name, value in sorted(deviations.items(), key=lambda x: x[1], reverse=True)[:4] if value >= 1]

    @staticmethod
    def _missing(modalities):
        return [m for m in MODALITY_NAMES if m not in modalities]

    def _recommendations(self, score, trend, quality, missing, context: AIContextSummary):
        out = ["Compare repeated measurements under similar conditions; a single session should not be interpreted in isolation."]
        if quality < .6: out.append("Complete additional available signal groups on future check-ins to improve data quality.")
        if missing: out.append("Missing signals are ignored rather than imputed as normal; complete more modalities when practical.")
        if context.pending_reminder_count: out.append("You have pending health-document reminders. Review them in Notifications and follow your clinician's instructions.")
        if trend == "DEGRADING" or score < 60: out.append("If a change persists or concerns you, discuss it with a qualified healthcare professional.")
        return out

    @staticmethod
    def _limitations(history_count, missing, context):
        out = ["Observational monitoring only; this system does not diagnose disease or make treatment decisions.", "Camera and microphone measurements can be affected by lighting, device position, background noise and recording quality."]
        if history_count < 5: out.append("The individual baseline is still developing; confidence should increase with repeated observations.")
        if missing: out.append("Missing modalities were not treated as normal; they were excluded from the fusion score.")
        if context.document_count: out.append("Uploaded documents provide user-provided context; extracted text is not a substitute for clinician review.")
        return out

    def analyze(self, user_id: UUID, payload: AIAnalysisRequest) -> AIAnalysisResponse:
        current = self._vector(payload)
        history = self._history(user_id)
        context = self._context(user_id)
        score, algorithm, confidence, deviations = self._model_score(current, [r[2] for r in history])
        previous = history[0][1].overall_score if history else None
        trend = self._trend(score, previous)
        modalities = self._modalities(current)
        missing = self._missing(modalities)
        quality = self._quality(current, payload)
        persistence = self._persistence(deviations, history)
        drivers = self._drivers(deviations)
        recommendations = self._recommendations(score, trend, quality, missing, context)
        limitations = self._limitations(len(history), missing, context)
        now = datetime.now(timezone.utc)
        explanation = f"The current session is {('broadly consistent' if score >= 80 else 'moderately different' if score >= 60 else 'substantially different')} from the personal baseline. Trend: {trend}. Persistence: {persistence}. The assessment used {len(modalities)} available signal groups and {context.past_history_count} reported history entries with {context.document_count} uploaded document(s) available as contextual information. This is an observational signal, not a diagnosis."

        check_in = DailyCheckIn(user_id=user_id, check_in_date=date.today(), status="completed", completed_at=now, extra_metadata={"source": "web_multimodal_check_in", "model_version": MODEL_VERSION, "context": context.model_dump()})
        self.db.add(check_in); self.db.flush()
        feature_reads = []
        for name, category in FEATURES:
            if name in current:
                value = current[name]
                self.db.add(BiomarkerFeature(check_in_id=check_in.id, feature_name=name, feature_category=category, feature_value=value, source_modality=category, extracted_at=now, extra_properties={"model_version": MODEL_VERSION}))
                feature_reads.append(BiomarkerFeatureRead(name=name, category=category, value=value, deviation=deviations.get(name)))

        self.db.add(HealthStabilityScore(check_in_id=check_in.id, overall_score=round(score, 2), trend_category=trend, confidence=round(confidence, 3), generated_at=now, explanation_summary=explanation, model_metadata={"model_name": MODEL_NAME, "model_version": MODEL_VERSION, "algorithm": algorithm, "baseline_observations": len(history), "data_quality_score": quality, "modalities_present": modalities, "missing_modalities": missing, "top_drivers": drivers, "recommendations": recommendations, "limitations": limitations, "persistence_signal": persistence, "source_duration_seconds": payload.source_duration_seconds, "voice_language": payload.voice_language, "context": context.model_dump()}))
        self.db.commit()
        return AIAnalysisResponse(check_in_id=check_in.id, overall_score=round(score, 2), trend=trend, confidence=round(confidence, 3), model_name=MODEL_NAME, model_version=MODEL_VERSION, baseline_observations=len(history), explanation=explanation, features=feature_reads, generated_at=now, data_quality_score=quality, modalities_present=modalities, top_drivers=drivers, recommendations=recommendations, limitations=limitations, missing_modalities=missing, persistence_signal=persistence, context=context)

    def history(self, user_id: UUID, limit=30):
        rows = self._history(user_id, limit)
        return AIHistoryResponse(items=[AIHistoryPoint(check_in_id=c.id, score=round(s.overall_score, 2), trend=s.trend_category, confidence=round(s.confidence, 3), generated_at=s.generated_at) for c, s, _ in reversed(rows)], baseline_observations=len(rows), model_name=MODEL_NAME, model_version=MODEL_VERSION)

    def latest(self, user_id: UUID):
        rows = self._history(user_id, 1)
        if not rows: return None
        c, s, _ = rows[0]
        features = self.db.execute(select(BiomarkerFeature).where(BiomarkerFeature.check_in_id == c.id)).scalars().all()
        m = s.model_metadata or {}
        return AIAnalysisResponse(check_in_id=c.id, overall_score=round(s.overall_score, 2), trend=s.trend_category, confidence=round(s.confidence, 3), model_name=str(m.get("model_name", MODEL_NAME)), model_version=str(m.get("model_version", MODEL_VERSION)), baseline_observations=int(m.get("baseline_observations", 0)), explanation=s.explanation_summary or "No explanation available.", features=[BiomarkerFeatureRead(name=f.feature_name, category=f.feature_category, value=float(f.feature_value), deviation=None) for f in features], generated_at=s.generated_at, data_quality_score=float(m.get("data_quality_score", 0)), modalities_present=list(m.get("modalities_present", [])), top_drivers=list(m.get("top_drivers", [])), recommendations=list(m.get("recommendations", [])), limitations=list(m.get("limitations", [])), missing_modalities=list(m.get("missing_modalities", [])), persistence_signal=str(m.get("persistence_signal", "INSUFFICIENT_HISTORY")), context=AIContextSummary(**m.get("context", {})))
