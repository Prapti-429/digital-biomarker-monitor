/**
 * Medication Regimen and TKI Adherence Tracker Component.
 *
 * Displays active prescribed TKI therapy (Imatinib, Dasatinib, etc.), dose details,
 * missed dose counters, and calculated adherence percentage gauges.
 */

import React from 'react';
import { MedicationRegimen } from '../types/clinical';

interface MedicationTrackerProps {
  medications: MedicationRegimen[];
}

export const MedicationTracker: React.FC<MedicationTrackerProps> = ({ medications }) => {
  if (medications.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-6 text-center text-slate-400 text-sm">
        No active TKI medication regimens prescribed.
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
      <h4 className="text-sm font-semibold text-slate-800 uppercase tracking-wider mb-2">
        Prescribed TKI Regimens & Adherence
      </h4>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {medications.map((med) => (
          <div key={med.id} className="border border-slate-200 rounded-lg p-4 bg-slate-50/50">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h5 className="font-bold text-slate-900 text-base">{med.medication_name}</h5>
                <p className="text-xs text-slate-500">
                  {med.dose} ({med.frequency}) &bull; {med.route}
                </p>
              </div>
              <span
                className={`text-xs px-2 py-0.5 rounded font-semibold ${
                  med.adherence_percentage >= 90
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {med.adherence_percentage}% Adherence
              </span>
            </div>

            <div className="mt-3 pt-3 border-t border-slate-200 flex justify-between text-xs text-slate-600">
              <span>Initiated: {new Date(med.start_date).toLocaleDateString()}</span>
              <span>Missed Doses: {med.missed_dose_counter}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};