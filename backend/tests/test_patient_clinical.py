"""
Patient Management & Clinical Telemetry Integration Tests.

Validates patient profile lifecycles, automated MRN generation, TKI medication
prescriptions, adherence log calculations, vital signs telemetry (with BMI math),
BCR-ABL1 quantitative PCR laboratory records, and RBAC security boundaries.
"""

import sys
from pathlib import Path

# Ensure backend root is on sys.path for Pytest execution
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from datetime import date
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models import User
from app.schemas.auth_enums import UserRole
from app.core.security import hash_password


@pytest.fixture
def test_clinician_user(db_session: Session) -> User:
    """Pre-seeds an active clinician user in the test database."""
    user = User(
        email="doctor@hospital.org",
        hashed_password=hash_password("DoctorPass123!"),
        full_name="Dr. Sarah Connor",
        role=UserRole.CLINICIAN,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_patient_user_2(db_session: Session) -> User:
    """Pre-seeds a second patient user to verify RBAC isolation."""
    user = User(
        email="patient2@example.com",
        hashed_password=hash_password("PatientPass123!"),
        full_name="John Doe",
        role=UserRole.PATIENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_auth_header(client: TestClient, email: str, password: str) -> dict[str, str]:
    """Helper utility to log in and return authorization Bearer headers."""
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == status.HTTP_200_OK
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# -----------------------------------------------------------------------------
# Patient Profile Lifecycle Tests
# -----------------------------------------------------------------------------
def test_create_patient_profile_and_mrn_generation(
    client: TestClient, test_patient_user: User
) -> None:
    """Tests patient profile creation and automated MRN assignment."""
    headers = get_auth_header(client, "patient@example.com", "SecurePassword123!")

    payload = {
        "user_id": test_patient_user.id,
        "first_name": "Jane",
        "last_name": "Patient",
        "date_of_birth": "1985-05-15",
        "sex": "Female",
        "height_cm": 168.0,
        "primary_diagnosis": "Chronic Myeloid Leukemia (CML)",
        "disease_phase": "Chronic Phase",
    }

    response = client.post("/api/v1/patients", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_id"] == test_patient_user.id
    assert data["first_name"] == "Jane"
    assert data["medical_record_number"].startswith("CML-")
    assert data["age"] > 0


def test_get_my_patient_profile(client: TestClient, test_patient_user: User) -> None:
    """Tests fetching current user's bound patient profile via /patients/me."""
    headers = get_auth_header(client, "patient@example.com", "SecurePassword123!")

    # Create profile
    client.post(
        "/api/v1/patients",
        json={
            "user_id": test_patient_user.id,
            "first_name": "Jane",
            "last_name": "Patient",
            "date_of_birth": "1985-05-15",
            "sex": "Female",
        },
        headers=headers,
    )

    # Fetch bound profile
    response = client.get("/api/v1/patients/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "Jane"


def test_rbac_patient_isolation(
    client: TestClient, test_patient_user: User, test_patient_user_2: User
) -> None:
    """Verifies a patient cannot view or access another patient's profile."""
    p1_headers = get_auth_header(client, "patient@example.com", "SecurePassword123!")
    p2_headers = get_auth_header(client, "patient2@example.com", "PatientPass123!")

    # Patient 1 creates profile
    p1_resp = client.post(
        "/api/v1/patients",
        json={
            "user_id": test_patient_user.id,
            "first_name": "Jane",
            "last_name": "Patient",
            "date_of_birth": "1985-05-15",
            "sex": "Female",
        },
        headers=p1_headers,
    )
    p1_id = p1_resp.json()["id"]

    # Patient 2 attempts to query Patient 1's profile -> HTTP 403 Forbidden
    response = client.get(f"/api/v1/patients/{p1_id}", headers=p2_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# -----------------------------------------------------------------------------
# Medication & Adherence Telemetry Tests
# -----------------------------------------------------------------------------
def test_medication_prescribing_and_adherence_tracking(
    client: TestClient, test_patient_user: User, test_clinician_user: User
) -> None:
    """Tests prescribing a TKI regimen (Imatinib) and calculating dosage adherence."""
    p_headers = get_auth_header(client, "patient@example.com", "SecurePassword123!")
    c_headers = get_auth_header(client, "doctor@hospital.org", "DoctorPass123!")

    # Create Patient Profile
    p_resp = client.post(
        "/api/v1/patients",
        json={
            "user_id": test_patient_user.id,
            "first_name": "Jane",
            "last_name": "Patient",
            "date_of_birth": "1985-05-15",
            "sex": "Female",
        },
        headers=p_headers,
    )
    patient_id = p_resp.json()["id"]

    # Clinician prescribes Imatinib 400mg Daily
    med_payload = {
        "patient_id": patient_id,
        "medication_name": "Imatinib",
        "drug_class": "Tyrosine Kinase Inhibitor",
        "dose": "400mg",
        "dose_value_mg": 400.0,
        "frequency": "Once Daily",
        "route": "Oral",
        "start_date": str(date.today()),
    }
    med_resp = client.post("/api/v1/medications/regimens", json=med_payload, headers=c_headers)
    assert med_resp.status_code == status.HTTP_201_CREATED
    regimen_id = med_resp.json()["id"]

    # Patient logs 1 taken dose and 1 missed dose
    client.post(
        "/api/v1/medications/adherence",
        json={
            "regimen_id": regimen_id,
            "scheduled_time": "2026-08-01T08:00:00Z",
            "was_taken": True,
        },
        headers=p_headers,
    )
    client.post(
        "/api/v1/medications/adherence",
        json={
            "regimen_id": regimen_id,
            "scheduled_time": "2026-08-02T08:00:00Z",
            "was_taken": False,
            "reason_missed": "Nausea",
        },
        headers=p_headers,
    )

    # Fetch updated regimen and check adherence percentage (1/2 = 50.0%)
    get_meds = client.get(f"/api/v1/medications/patient/{patient_id}", headers=p_headers)
    assert get_meds.status_code == status.HTTP_200_OK
    regimens = get_meds.json()
    assert len(regimens) == 1
    assert regimens[0]["adherence_percentage"] == 50.0
    assert regimens[0]["missed_dose_counter"] == 1


# -----------------------------------------------------------------------------
# Vital Signs Telemetry & Lab PCR Diagnostics Tests
# -----------------------------------------------------------------------------
def test_vital_signs_and_automatic_bmi_calculation(
    client: TestClient, test_patient_user: User
) -> None:
    """Tests recording vitals and verifying automated BMI derivation (Weight / Height^2)."""
    headers = get_auth_header(client, "patient@example.com", "SecurePassword123!")

    # Create Patient Profile with Height = 170 cm (1.7 m)
    p_resp = client.post(
        "/api/v1/patients",
        json={
            "user_id": test_patient_user.id,
            "first_name": "Jane",
            "last_name": "Patient",
            "date_of_birth": "1985-05-15",
            "sex": "Female",
            "height_cm": 170.0,
        },
        headers=headers,
    )
    patient_id = p_resp.json()["id"]

    # Record Weight = 68 kg -> Expected BMI = 68 / (1.7^2) = 23.53
    vitals_payload = {
        "patient_id": patient_id,
        "weight_kg": 68.0,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "heart_rate_bpm": 72,
        "spo2_percentage": 98.5,
    }
    v_resp = client.post("/api/v1/clinical/vitals", json=vitals_payload, headers=headers)
    assert v_resp.status_code == status.HTTP_201_CREATED
    assert v_resp.json()["bmi"] == 23.53


def test_bcr_abl_pcr_laboratory_record(
    client: TestClient, test_patient_user: User, test_clinician_user: User
) -> None:
    """Tests recording CML quantitative PCR BCR-ABL1 % IS molecular biomarkers."""
    p_headers = get_auth_header(client, "patient@example.com", "SecurePassword123!")
    c_headers = get_auth_header(client, "doctor@hospital.org", "DoctorPass123!")

    p_resp = client.post(
        "/api/v1/patients",
        json={
            "user_id": test_patient_user.id,
            "first_name": "Jane",
            "last_name": "Patient",
            "date_of_birth": "1985-05-15",
            "sex": "Female",
        },
        headers=p_headers,
    )
    patient_id = p_resp.json()["id"]

    # Clinician records major molecular response PCR result (BCR-ABL1 = 0.05% IS)
    lab_payload = {
        "patient_id": patient_id,
        "test_category": "Molecular Diagnostics",
        "test_name": "BCR-ABL1 Major (p210) Quantitative PCR",
        "numerical_value": 0.05,
        "unit": "% IS",
        "reference_range": "< 0.1% IS (MMR)",
        "is_abnormal": False,
        "collection_date": "2026-08-01",
        "laboratory_name": "Central Molecular Oncology Lab",
    }
    lab_resp = client.post("/api/v1/clinical/labs", json=lab_payload, headers=c_headers)
    assert lab_resp.status_code == status.HTTP_201_CREATED

    # Patient retrieves lab history
    get_labs = client.get(f"/api/v1/clinical/labs/patient/{patient_id}", headers=p_headers)
    assert get_labs.status_code == status.HTTP_200_OK
    items = get_labs.json()["items"]
    assert len(items) == 1
    assert items[0]["numerical_value"] == 0.05
    assert items[0]["unit"] == "% IS"