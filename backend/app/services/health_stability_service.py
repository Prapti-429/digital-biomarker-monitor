"""
Multi-Factor Health Stability Score (HSS) Analytics Service.

Aggregates 30-day telemetry across TKI medication adherence, vital signs,
symptom burden, and nutrition logs to compute dynamic composite scores.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.medication import MedicationRegimen, MedicationAdherenceLog
from app.db.models.vitals import VitalSigns
from app.db.models.symptoms import SymptomLog
from app.db.models.lifestyle import NutritionLog
from app.schemas.health_stability_schemas import (
    HealthStabilityDimensionScore,
    HealthStabilityScoreRead,
    HealthStabilityHistoricalPoint,
    HealthStabilityTrendResponse,
)


class HealthStabilityService:
    """Calculates multi-dimensional health stability indices for CML and oncology patients."""

    WEIGHT_MEDICATION = 0.35
    WEIGHT_VITALS = 0.25
    WEIGHT_SYMPTOMS = 0.25
    WEIGHT_NUTRITION = 0.15

    def __init__(self, db: Session):
        self.db = db

    def calculate_patient_hss(self, patient_id: uuid.UUID) -> HealthStabilityScoreRead:
        """Calculates current composite Health Stability Score (0-100) for a patient."""
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # Data density tracking for confidence calculation
        available_domains = 0

        # 1. Dimension 1: Medication Adherence (35%)
        med_score, med_status, med_factor, med_has_data = self._calc_medication_score(patient_id)
        if med_has_data:
            available_domains += 1

        # 2. Dimension 2: Vital Signs Stability (25%)
        vitals_score, vitals_status, vitals_factor, vitals_has_data = self._calc_vitals_score(patient_id, thirty_days_ago)
        if vitals_has_data:
            available_domains += 1

        # 3. Dimension 3: Symptom Burden Index (25%)
        sym_score, sym_status, sym_factor, sym_has_data = self._calc_symptoms_score(patient_id, thirty_days_ago)
        if sym_has_data:
            available_domains += 1

        # 4. Dimension 4: Nutrition & Hydration Score (15%)
        nut_score, nut_status, nut_factor, nut_has_data = self._calc_nutrition_score(patient_id, thirty_days_ago)
        if nut_has_data:
            available_domains += 1

        # Calculate Weighted Composite Score
        overall_score = round(
            (med_score * self.WEIGHT_MEDICATION) +
            (vitals_score * self.WEIGHT_VITALS) +
            (sym_score * self.WEIGHT_SYMPTOMS) +
            (nut_score * self.WEIGHT_NUTRITION),
            1
        )

        # Confidence Score based on telemetry domain completeness
        confidence_score = round((available_domains / 4.0) * 100.0, 1)

        # Determine Tier
        if overall_score >= 80.0:
            stability_tier = "High Stability"
        elif overall_score >= 60.0:
            stability_tier = "Moderate Risk"
        else:
            stability_tier = "High Risk"

        # Determine Primary Risk Driver
        dimensions = [
            HealthStabilityDimensionScore(
                dimension="Medication Adherence",
                score=med_score,
                weight=self.WEIGHT_MEDICATION,
                weighted_contribution=round(med_score * self.WEIGHT_MEDICATION, 1),
                status=med_status,
                key_factor=med_factor,
            ),
            HealthStabilityDimensionScore(
                dimension="Vital Signs",
                score=vitals_score,
                weight=self.WEIGHT_VITALS,
                weighted_contribution=round(vitals_score * self.WEIGHT_VITALS, 1),
                status=vitals_status,
                key_factor=vitals_factor,
            ),
            HealthStabilityDimensionScore(
                dimension="Symptom Burden",
                score=sym_score,
                weight=self.WEIGHT_SYMPTOMS,
                weighted_contribution=round(sym_score * self.WEIGHT_SYMPTOMS, 1),
                status=sym_status,
                key_factor=sym_factor,
            ),
            HealthStabilityDimensionScore(
                dimension="Nutrition & Hydration",
                score=nut_score,
                weight=self.WEIGHT_NUTRITION,
                weighted_contribution=round(nut_score * self.WEIGHT_NUTRITION, 1),
                status=nut_status,
                key_factor=nut_factor,
            ),
        ]

        # Lowest scoring dimension is the primary risk driver
        lowest_dim = min(dimensions, key=lambda d: d.score)
        primary_risk_driver = lowest_dim.dimension if lowest_dim.score < 75.0 else "None (All Sub-systems Optimal)"

        # Clinical narrative explanation
        explanation = (
            f"Patient composite stability score is {overall_score}/100 ({stability_tier}). "
            f"Adherence score is {med_score:.0f}%, vitals stability is {vitals_score:.0f}%, "
            f"and symptom burden score is {sym_score:.0f}%. "
            f"Primary focus area: {primary_risk_driver}."
        )

        return HealthStabilityScoreRead(
            patient_id=patient_id,
            assessment_timestamp=now,
            overall_score=overall_score,
            stability_tier=stability_tier,
            trend_direction="Stable",
            confidence_score=confidence_score,
            primary_risk_driver=primary_risk_driver,
            dimensions=dimensions,
            explanation=explanation,
        )

    # -------------------------------------------------------------------------
    # Helper Sub-Calculators
    # -------------------------------------------------------------------------
    def _calc_medication_score(self, patient_id: uuid.UUID) -> tuple[float, str, str, bool]:
        stmt = select(MedicationRegimen).filter(
            MedicationRegimen.patient_id == patient_id,
            MedicationRegimen.is_active == True,
        )
        regimens = list(self.db.scalars(stmt).all())
        if not regimens:
            return 80.0, "Optimal", "No active medication regimens recorded", False

        avg_adherence = sum(r.adherence_percentage for r in regimens) / len(regimens)
        status = "Optimal" if avg_adherence >= 90.0 else ("Moderate" if avg_adherence >= 75.0 else "Poor")
        factor = f"30-day TKI adherence is {avg_adherence:.1f}% across {len(regimens)} active regimen(s)"
        return round(avg_adherence, 1), status, factor, True

    def _calc_vitals_score(self, patient_id: uuid.UUID, since: datetime) -> tuple[float, str, str, bool]:
        stmt = (
            select(VitalSigns)
            .filter(VitalSigns.patient_id == patient_id)
            .filter(VitalSigns.recorded_at >= since)
            .order_by(VitalSigns.recorded_at.desc())
        )
        vitals_list = list(self.db.scalars(stmt).all())
        if not vitals_list:
            return 85.0, "Optimal", "No vital signs telemetry in past 30 days", False

        penalties = 0.0
        for v in vitals_list:
            if v.systolic_bp and (v.systolic_bp > 140 or v.systolic_bp < 90):
                penalties += 5.0
            if v.spo2_percentage and v.spo2_percentage < 95.0:
                penalties += 15.0
            if v.heart_rate_bpm and (v.heart_rate_bpm > 100 or v.heart_rate_bpm < 50):
                penalties += 5.0

        score = max(0.0, min(100.0, 100.0 - (penalties / len(vitals_list))))
        status = "Optimal" if score >= 85.0 else ("Moderate" if score >= 65.0 else "Poor")
        factor = f"Evaluated {len(vitals_list)} vital sign entries; average variance penalty is {penalties/len(vitals_list):.1f} pts"
        return round(score, 1), status, factor, True

    def _calc_symptoms_score(self, patient_id: uuid.UUID, since: datetime) -> tuple[float, str, str, bool]:
        stmt = (
            select(SymptomLog)
            .filter(SymptomLog.patient_id == patient_id)
            .filter(SymptomLog.recorded_at >= since)
        )
        symptoms = list(self.db.scalars(stmt).all())
        if not symptoms:
            return 95.0, "Optimal", "No active symptoms reported in past 30 days", True

        total_severity = sum(s.severity for s in symptoms)
        avg_severity = total_severity / len(symptoms) # Severity 1 (mild) to 10 (severe)
        score = max(0.0, 100.0 - (avg_severity * 9.0))
        status = "Optimal" if score >= 80.0 else ("Moderate" if score >= 60.0 else "Poor")
        factor = f"{len(symptoms)} symptom events logged with mean severity {avg_severity:.1f}/10"
        return round(score, 1), status, factor, True

    def _calc_nutrition_score(self, patient_id: uuid.UUID, since: datetime) -> tuple[float, str, str, bool]:
        stmt = (
            select(NutritionLog)
            .filter(NutritionLog.patient_id == patient_id)
            .filter(NutritionLog.log_date >= since.date())
        )
        logs = list(self.db.scalars(stmt).all())
        if not logs:
            return 75.0, "Moderate", "No nutrition logs recorded in past 30 days", False

        adequate_hydration_count = sum(1 for l in logs if (l.fluid_intake_ml or 0) >= 2000.0)
        hydration_rate = (adequate_hydration_count / len(logs)) * 100.0
        status = "Optimal" if hydration_rate >= 80.0 else "Moderate"
        factor = f"Target fluid intake met on {adequate_hydration_count}/{len(logs)} logged days ({hydration_rate:.0f}%)"
        return round(hydration_rate, 1), status, factor, True