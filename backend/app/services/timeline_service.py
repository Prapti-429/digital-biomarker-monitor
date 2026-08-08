"""
Unified Longitudinal Clinical Master Timeline Aggregator Service.

Querying Vitals, Labs, Symptoms, Medication Adherence, Nutrition, and File Uploads
and normalizing them into a chronological stream.
"""

from datetime import datetime, timezone
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.vitals import VitalSigns
from app.db.models.labs import LabResult
from app.db.models.symptoms import SymptomLog
from app.db.models.medication import MedicationAdherenceLog, MedicationRegimen
from app.db.models.lifestyle import NutritionLog
from app.db.models.file_upload import FileUploadRecord
from app.schemas.timeline_schemas import TimelineEventItem, ClinicalTimelineResponse


class ClinicalTimelineService:
    """Aggregates disparate clinical telemetry tables into a unified chronological stream."""

    def __init__(self, db: Session):
        self.db = db

    def get_patient_timeline(
        self,
        patient_id: uuid.UUID,
        event_types: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 30,
    ) -> ClinicalTimelineResponse:
        """Fetches and merges all temporal clinical records for a target patient."""
        all_events: List[TimelineEventItem] = []

        # 1. Gather Vital Signs
        if not event_types or "VITAL_SIGNS" in event_types:
            vitals_stmt = select(VitalSigns).filter(VitalSigns.patient_id == patient_id)
            for v in self.db.scalars(vitals_stmt).all():
                severity = "normal"
                if (v.systolic_bp and v.systolic_bp > 140) or (v.spo2_percentage and v.spo2_percentage < 95.0):
                    severity = "warning"

                all_events.append(
                    TimelineEventItem(
                        event_id=str(v.id),
                        event_type="VITAL_SIGNS",
                        timestamp=v.recorded_at,
                        title="Vital Signs Recorded",
                        subtitle=f"BP: {v.systolic_bp or '--'}/{v.diastolic_bp or '--'} mmHg, HR: {v.heart_rate_bpm or '--'} bpm",
                        severity_indicator=severity,
                        details={
                            "weight_kg": v.weight_kg,
                            "spo2_percentage": v.spo2_percentage,
                            "bmi": v.bmi,
                        },
                    )
                )

        # 2. Gather Lab & Biomarker Results
        if not event_types or "LAB_RESULT" in event_types:
            labs_stmt = select(LabResult).filter(LabResult.patient_id == patient_id)
            for lab in self.db.scalars(labs_stmt).all():
                dt = datetime.combine(lab.collection_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                severity = "alert" if lab.is_abnormal else "normal"

                all_events.append(
                    TimelineEventItem(
                        event_id=str(lab.id),
                        event_type="LAB_RESULT",
                        timestamp=dt,
                        title=lab.test_name,
                        subtitle=f"Value: {lab.numerical_value or lab.text_value or '--'} {lab.unit or ''}",
                        severity_indicator=severity,
                        details={
                            "test_category": lab.test_category,
                            "reference_range": lab.reference_range,
                            "laboratory_name": lab.laboratory_name,
                        },
                    )
                )

        # 3. Gather Symptom Logs
        if not event_types or "SYMPTOM" in event_types:
            sym_stmt = select(SymptomLog).filter(SymptomLog.patient_id == patient_id)
            for s in self.db.scalars(sym_stmt).all():
                severity = "alert" if s.severity >= 7 else ("warning" if s.severity >= 4 else "normal")

                all_events.append(
                    TimelineEventItem(
                        event_id=str(s.id),
                        event_type="SYMPTOM",
                        timestamp=s.recorded_at,
                        title=f"Symptom: {s.symptom_name}",
                        subtitle=f"Severity: {s.severity}/10 ({s.progression or 'Stable'})",
                        severity_indicator=severity,
                        details={
                            "frequency": s.frequency,
                            "patient_notes": s.patient_notes,
                        },
                    )
                )

        # 4. Gather Medication Adherence
        if not event_types or "MEDICATION" in event_types:
            med_stmt = (
                select(MedicationAdherenceLog, MedicationRegimen.medication_name)
                .join(MedicationRegimen, MedicationAdherenceLog.regimen_id == MedicationRegimen.id)
                .filter(MedicationRegimen.patient_id == patient_id)
            )
            for log, med_name in self.db.execute(med_stmt).all():
                severity = "normal" if log.was_taken else "warning"

                all_events.append(
                    TimelineEventItem(
                        event_id=str(log.id),
                        event_type="MEDICATION",
                        timestamp=log.scheduled_time,
                        title=f"Medication: {med_name}",
                        subtitle="Dose Taken" if log.was_taken else f"Missed ({log.reason_missed or 'No reason'})",
                        severity_indicator=severity,
                        details={
                            "was_taken": log.was_taken,
                            "taken_time": log.taken_time.isoformat() if log.taken_time else None,
                        },
                    )
                )

        # 5. Gather Nutrition Logs
        if not event_types or "NUTRITION" in event_types:
            nut_stmt = select(NutritionLog).filter(NutritionLog.patient_id == patient_id)
            for n in self.db.scalars(nut_stmt).all():
                dt = datetime.combine(n.log_date, datetime.min.time()).replace(tzinfo=timezone.utc)

                all_events.append(
                    TimelineEventItem(
                        event_id=str(n.id),
                        event_type="NUTRITION",
                        timestamp=dt,
                        title="Daily Nutrition Logged",
                        subtitle=f"Calories: {n.calories_kcal or '--'} kcal, Fluids: {n.fluid_intake_ml or '--'} mL",
                        severity_indicator="normal",
                        details={
                            "protein_grams": n.protein_grams,
                            "skipped_meals": getattr(n, "skipped_meals", False),
                        },
                    )
                )

        # 6. Gather File Upload Assets
        if not event_types or "FILE_UPLOAD" in event_types:
            file_stmt = select(FileUploadRecord).filter(FileUploadRecord.patient_id == patient_id)
            for f in self.db.scalars(file_stmt).all():
                all_events.append(
                    TimelineEventItem(
                        event_id=str(f.id),
                        event_type="FILE_UPLOAD",
                        timestamp=f.created_at,
                        title=f"Biomarker File Uploaded ({f.file_category.upper()})",
                        subtitle=f.original_filename,
                        severity_indicator="info",
                        details={
                            "file_size_bytes": f.file_size_bytes,
                            "mime_type": f.mime_type,
                        },
                    )
                )

        # Sort all aggregated events in descending order (most recent first)
        all_events.sort(key=lambda x: x.timestamp, reverse=True)

        total_events = len(all_events)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_events = all_events[start_idx:end_idx]

        return ClinicalTimelineResponse(
            patient_id=patient_id,
            total_events=total_events,
            page=page,
            page_size=page_size,
            events=paginated_events,
        )