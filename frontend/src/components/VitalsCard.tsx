/**
 * Vital Signs Telemetry Summary Component.
 *
 * Displays latest physical vital signs, blood pressure ratio, oxygen saturation, and computed BMI.
 */

import React from 'react';
import { VitalSigns } from '../types/clinical';

interface VitalsCardProps {
  vitals?: VitalSigns;
}

export const VitalsCard: React.FC<VitalsCardProps> = ({ vitals }) => {
  if (!vitals) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-5 text-center text-slate-400 text-sm">
        No vital signs recorded yet.
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h4 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">
          Latest Vital Signs
        </h4>
        <span className="text-xs text-slate-400">
          {new Date(vitals.recorded_at).toLocaleString()}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <p className="text-xs text-slate-500">Blood Pressure</p>
          <p className="text-lg font-bold text-slate-900 mt-1">
            {vitals.systolic_bp && vitals.diastolic_bp
              ? `${vitals.systolic_bp}/${vitals.diastolic_bp}`
              : '--/--'}
            <span className="text-xs font-normal text-slate-400 ml-1">mmHg</span>
          </p>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <p className="text-xs text-slate-500">Heart Rate</p>
          <p className="text-lg font-bold text-slate-900 mt-1">
            {vitals.heart_rate_bpm ?? '--'}
            <span className="text-xs font-normal text-slate-400 ml-1">bpm</span>
          </p>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <p className="text-xs text-slate-500">SpO₂ Saturation</p>
          <p className="text-lg font-bold text-slate-900 mt-1">
            {vitals.spo2_percentage ?? '--'}
            <span className="text-xs font-normal text-slate-400 ml-1">%</span>
          </p>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <p className="text-xs text-slate-500">Weight & BMI</p>
          <p className="text-lg font-bold text-slate-900 mt-1">
            {vitals.weight_kg ?? '--'}
            <span className="text-xs font-normal text-slate-400 ml-1">
              kg {vitals.bmi ? `(${vitals.bmi} BMI)` : ''}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};