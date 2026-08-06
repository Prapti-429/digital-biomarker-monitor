/**
 * Patient Summary Card Component.
 *
 * Renders patient demographics, MRN badge, biological age, and CML disease phase indicator.
 */

import React from 'react';
import { Patient } from '../types/clinical';

interface PatientCardProps {
  patient: Patient;
  onSelect?: (patientId: string) => void;
}

export const PatientCard: React.FC<PatientCardProps> = ({ patient, onSelect }) => {
  const getPhaseBadgeColor = (phase?: string) => {
    switch (phase) {
      case 'Chronic Phase':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'Accelerated Phase':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'Blast Phase':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  return (
    <div
      onClick={() => onSelect && onSelect(patient.id)}
      className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow cursor-pointer flex flex-col justify-between"
    >
      <div>
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">
              {patient.last_name}, {patient.first_name}
            </h3>
            <p className="text-xs text-slate-500 font-mono mt-0.5">
              MRN: {patient.medical_record_number || 'N/A'}
            </p>
          </div>
          <span
            className={`text-xs font-medium px-2.5 py-1 rounded-full border ${getPhaseBadgeColor(
              patient.disease_phase
            )}`}
          >
            {patient.disease_phase || 'Phase Unspecified'}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 mb-4">
          <div>
            <span className="font-medium text-slate-400">Age/Sex:</span> {patient.age}y / {patient.sex}
          </div>
          <div>
            <span className="font-medium text-slate-400">Diagnosis:</span> {patient.primary_diagnosis}
          </div>
          {patient.height_cm && (
            <div>
              <span className="font-medium text-slate-400">Height:</span> {patient.height_cm} cm
            </div>
          )}
          {patient.current_disease_status && (
            <div>
              <span className="font-medium text-slate-400">Status:</span> {patient.current_disease_status}
            </div>
          )}
        </div>
      </div>

      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>Enrolled: {new Date(patient.created_at).toLocaleDateString()}</span>
        <span className="text-indigo-600 font-medium hover:underline">View Chart &rarr;</span>
      </div>
    </div>
  );
};