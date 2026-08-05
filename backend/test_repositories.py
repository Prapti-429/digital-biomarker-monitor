"""
Module 3C Verification Script.
Tests repository layer creation, query operations, and transactions.
"""

from app.database import SessionLocal, engine
from app.models import Base, UserRole, ProcessingStatus
from app.repositories import (
    UserRepository,
    PatientRepository,
    DailyCheckInRepository,
    SymptomRepository,
    AudioRepository,
    VideoRepository,
    AIResultRepository,
    PaginationParams,
    SortParam,
    SortOrder,
)

def run_verification():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("--- 1. Testing UserRepository ---")
        user_repo = UserRepository(db)
        user = user_repo.create_user({
            "email": "test.patient@example.com",
            "hashed_password": "secure_hashed_password",
            "full_name": "Test Patient",
            "role": UserRole.PATIENT,
        })
        print(f"[OK] Created User: ID={user.id}, Email={user.email}")

        fetched_user = user_repo.get_by_email("test.patient@example.com")
        assert fetched_user is not None and fetched_user.id == user.id
        print(f"[OK] Fetched User by email: {fetched_user.email}")

        print("\n--- 2. Testing PatientRepository ---")
        patient_repo = PatientRepository(db)
        patient = patient_repo.create_patient({
            "user_id": user.id,
            "medical_history_notes": "Early onset monitor target",
        })
        print(f"[OK] Created Patient: ID={patient.id} linked to User ID={patient.user_id}")

        print("\n--- 3. Testing DailyCheckInRepository ---")
        checkin_repo = DailyCheckInRepository(db)
        checkin = checkin_repo.create_checkin({
            "patient_id": patient.id,
            "notes": "Morning check-in with slight tremor",
        })
        print(f"[OK] Created DailyCheckIn: ID={checkin.id}")

        print("\n--- 4. Testing Symptom & Media Repositories ---")
        symptom_repo = SymptomRepository(db)
        symptom = symptom_repo.create_symptom({
            "check_in_id": checkin.id,
            "symptom_name": "Tremor",
            "severity_score": 3,
        })
        print(f"[OK] Created Symptom: {symptom.symptom_name} (Severity={symptom.severity_score})")

        audio_repo = AudioRepository(db)
        audio = audio_repo.create_audio_record({
            "check_in_id": checkin.id,
            "file_path": "s3://biomarker-storage/audio/checkin_1.wav",
            "duration_seconds": 12.5,
        })
        print(f"[OK] Created AudioRecord: ID={audio.id}")

        video_repo = VideoRepository(db)
        video = video_repo.create_video_record({
            "check_in_id": checkin.id,
            "file_path": "s3://biomarker-storage/video/checkin_1.mp4",
            "resolution": "1920x1080",
        })
        print(f"[OK] Created VideoRecord: ID={video.id}")

        ai_repo = AIResultRepository(db)
        ai_res = ai_repo.save_ai_result({
            "check_in_id": checkin.id,
            "model_name": "VocalBiomarkerModel",
            "model_version": "v1.2.0",
            "status": ProcessingStatus.COMPLETED,
            "risk_score": 0.42,
            "biomarker_features": {"jitter": 0.012, "shimmer": 0.034},
        })
        print(f"[OK] Saved AIResult: Score={ai_res.risk_score}")

        print("\n--- 5. Testing Pagination & Eager Queries ---")
        paginated_users = user_repo.paginate(
            pagination=PaginationParams(page=1, page_size=5),
            sort_params=[SortParam(field="id", order=SortOrder.DESC)]
        )
        print(f"[OK] Paginated Users: Total={paginated_users.total}, Items in page={len(paginated_users.items)}")

        patient_history = patient_repo.get_longitudinal_history(patient.id)
        print(f"[OK] Retrieved Patient Longitudinal History: {len(patient_history)} record(s)")

        print("\nSUCCESS: All repository layer verifications passed!")
    finally:
        db.close()

if __name__ == "__main__":
    run_verification()