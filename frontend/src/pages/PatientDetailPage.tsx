/**
 * Comprehensive Patient Chart & Telemetry Page Component.
 *
 * Displays detailed demographics, active TKI regimens, laboratory history
 * (including BCR-ABL % IS PCR trends), and vital signs telemetry.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { clinicalService } from '../services/clinicalService';
import { Patient, MedicationRegimen, VitalSigns, LabResult } from '../types/clinical';
import { VitalsCard } from '../components/VitalsCard';
import { LabResultsTable } from '../components/LabResultsTable';
import { MedicationTracker } from '../components/MedicationTracker';

export const PatientDetailPage: React.FC = () => {
  const { patientId } = useParams<{ patientId: string }>();
  const navigate = useNavigate();

  const [patient, setPatient] = useState<Patient | null>(null);
  const [medications, setMedications] = useState<MedicationRegimen[]>([]);
  const [vitals, setVitals] = useState<VitalSigns | undefined>(undefined);
  const [labs, setLabs] = useState<LabResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadPatientChart = useCallback(async () => {
    if (!patientId) return;
    setIsLoading(true);
    try {
      const [patientData, medData, vitalsData, labsData] = await Promise.all([
        clinicalService.getPatientById(patientId),
        clinicalService.getPatientMedications(patientId),
        clinicalService.getPatientVitals(patientId, 1, 1),
        clinicalService.getPatientLabs(patientId, undefined, 1, 20),
      ]);

      setPatient(patientData);
      setMedications(medData);
      setVitals(vitalsData.items[0]);
      setLabs(labsData.items);
    } catch (err) {
      console.error('Failed to load patient chart details:', err);
    } finally {
      setIsLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    loadPatientChart();
  }, [loadPatientChart]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="p-8 max-w-xl mx-auto text-center">
        <h2 className="text-xl font-bold text-slate-800">Patient Record Not Found</h2>
        <button
          onClick={() => navigate('/patients')}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm"
        >
          Back to Directory
        </button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <button
            onClick={() => navigate('/patients')}
            className="text-xs text-indigo-600 font-medium hover:underline mb-2 block"
          >
            &larr; Back to Patient Directory
          </button>
          <h1 className="text-2xl font-bold text-slate-900">
            {patient.first_name} {patient.last_name}
          </h1>
          <p className="text-xs text-slate-500 font-mono mt-1">
            MRN: {patient.medical_record_number} &bull; Age: {patient.age}y &bull; Sex: {patient.sex}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold px-3 py-1.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
            {patient.primary_diagnosis}
          </span>
          <span className="text-xs font-semibold px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            {patient.disease_phase}
          </span>
        </div>
      </div>

      {/* Grid Layout for Clinical Telemetry */}
      <div className="space-y-6">
        <VitalsCard vitals={vitals} />
        <MedicationTracker medications={medications} />
        <LabResultsTable labs={labs} />
      </div>
    </div>
  );
};