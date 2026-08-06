/**
 * Clinical Data Layer TypeScript Interfaces.
 *
 * Defines type contracts matching Pydantic DTOs for patients, vitals,
 * labs (BCR-ABL1 PCR), medication regimens, and symptoms.
 */

export interface Patient {
  id: string;
  user_id: number;
  medical_record_number?: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  age: number;
  sex: string;
  gender?: string;
  height_cm?: number;
  ethnicity?: string;
  blood_group?: string;
  preferred_language: string;
  time_zone: string;
  smoking_status?: string;
  alcohol_use?: string;
  occupation?: string;
  education_level?: string;
  emergency_contact_name?: string;
  emergency_contact_relationship?: string;
  emergency_contact_phone?: string;
  primary_diagnosis: string;
  secondary_diagnosis?: string;
  disease_phase?: string; // e.g., "Chronic Phase", "Accelerated Phase", "Blast Phase"
  disease_stage?: string;
  date_of_diagnosis?: string;
  current_disease_status?: string;
  treatment_phase?: string;
  hospital_affinity?: string;
  treating_physician_id?: number;
  clinical_notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface PatientListResponse {
  items: Patient[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface MedicationRegimen {
  id: string;
  patient_id: string;
  medication_name: string;
  drug_class: string;
  dose: string;
  dose_value_mg: number;
  frequency: string;
  route: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  missed_dose_counter: number;
  adherence_percentage: number;
  prescribing_clinician_id?: number;
  instructions?: string;
  side_effects_noted?: string;
  created_at: string;
  updated_at?: string;
}

export interface VitalSigns {
  id: string;
  patient_id: string;
  recorded_at: string;
  weight_kg?: number;
  systolic_bp?: number;
  diastolic_bp?: number;
  heart_rate_bpm?: number;
  respiratory_rate?: number;
  temperature_celsius?: number;
  spo2_percentage?: number;
  bmi?: number;
  pain_score?: number;
  fatigue_score?: number;
  activity_level?: string;
  measurement_source: string;
  notes?: string;
  created_at: string;
}

export interface VitalSignsListResponse {
  items: VitalSigns[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface LabResult {
  id: string;
  patient_id: string;
  test_category: string;
  test_name: string;
  numerical_value?: number;
  text_value?: string;
  unit?: string;
  reference_range?: string;
  is_abnormal?: boolean;
  collection_date: string;
  laboratory_name?: string;
  verification_status: string;
  clinician_comments?: string;
  created_at: string;
}

export interface LabResultListResponse {
  items: LabResult[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface SymptomLog {
  id: string;
  patient_id: string;
  symptom_name: string;
  severity: number;
  frequency?: string;
  duration?: string;
  onset?: string;
  progression?: string;
  patient_notes?: string;
  recorded_at: string;
}

export interface SymptomLogListResponse {
  items: SymptomLog[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}