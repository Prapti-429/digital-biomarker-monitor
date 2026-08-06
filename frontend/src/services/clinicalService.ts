/**
 * Clinical Data API Client Service.
 *
 * Encapsulates versioned REST calls for patient rosters, vital signs,
 * laboratory PCR values, TKI regimens, and symptoms.
 */

import { api } from './api';
import {
  Patient,
  PatientListResponse,
  MedicationRegimen,
  VitalSigns,
  VitalSignsListResponse,
  LabResultListResponse,
  SymptomLogListResponse,
} from '../types/clinical';

export const clinicalService = {
  // Patient Profile Endpoints
  async searchPatients(params?: {
    q?: string;
    clinician_id?: number;
    disease_phase?: string;
    page?: number;
    page_size?: number;
  }): Promise<PatientListResponse> {
    const response = await api.get<PatientListResponse>('/patients', { params });
    return response.data;
  },

  async getPatientById(patientId: string): Promise<Patient> {
    const response = await api.get<Patient>(`/patients/${patientId}`);
    return response.data;
  },

  async getMyPatientProfile(): Promise<Patient> {
    const response = await api.get<Patient>('/patients/me');
    return response.data;
  },

  // Medication Regimens & Adherence
  async getPatientMedications(patientId: string, activeOnly = false): Promise<MedicationRegimen[]> {
    const response = await api.get<MedicationRegimen[]>(`/medications/patient/${patientId}`, {
      params: { active_only: activeOnly },
    });
    return response.data;
  },

  async logAdherence(payload: {
    regimen_id: string;
    scheduled_time: string;
    taken_time?: string;
    was_taken: boolean;
    reason_missed?: string;
  }): Promise<void> {
    await api.post('/medications/adherence', payload);
  },

  // Vital Signs Telemetry
  async getPatientVitals(patientId: string, page = 1, pageSize = 20): Promise<VitalSignsListResponse> {
    const response = await api.get<VitalSignsListResponse>(`/clinical/vitals/patient/${patientId}`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  async recordVitals(payload: Record<string, unknown>): Promise<VitalSigns> {
    const response = await api.post<VitalSigns>('/clinical/vitals', payload);
    return response.data;
  },

  // Laboratory & Biomarker Results
  async getPatientLabs(patientId: string, category?: string, page = 1, pageSize = 20): Promise<LabResultListResponse> {
    const response = await api.get<LabResultListResponse>(`/clinical/labs/patient/${patientId}`, {
      params: { category, page, page_size: pageSize },
    });
    return response.data;
  },

  // Symptom Logging
  async getPatientSymptoms(patientId: string, page = 1, pageSize = 20): Promise<SymptomLogListResponse> {
    const response = await api.get<SymptomLogListResponse>(`/clinical/symptoms/patient/${patientId}`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
};