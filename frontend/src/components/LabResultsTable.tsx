/**
 * Laboratory Results and Molecular Response Tracker Component.
 *
 * Displays laboratory test histories with highlighting for BCR-ABL1 % IS quantitative PCR molecular results.
 */

import React from 'react';
import { LabResult } from '../types/clinical';

interface LabResultsTableProps {
  labs: LabResult[];
}

export const LabResultsTable: React.FC<LabResultsTableProps> = ({ labs }) => {
  if (labs.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-6 text-center text-slate-400 text-sm">
        No laboratory or PCR results recorded.
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      <div className="p-4 border-b border-slate-100 flex justify-between items-center">
        <h4 className="text-sm font-semibold text-slate-800 uppercase tracking-wider">
          Laboratory & Molecular Biomarkers
        </h4>
        <span className="text-xs text-slate-400">{labs.length} records</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-50 text-xs text-slate-500 uppercase tracking-wider border-b border-slate-100">
            <tr>
              <th className="px-4 py-3">Collection Date</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Test Name</th>
              <th className="px-4 py-3">Value / Result</th>
              <th className="px-4 py-3">Ref. Range</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {labs.map((lab) => {
              const isPcr = lab.test_name.toLowerCase().includes('bcr-abl');
              return (
                <tr key={lab.id} className={isPcr ? 'bg-indigo-50/30 font-medium' : 'hover:bg-slate-50/50'}>
                  <td className="px-4 py-3 whitespace-nowrap text-xs text-slate-500">
                    {new Date(lab.collection_date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">{lab.test_category}</td>
                  <td className="px-4 py-3 text-slate-900 font-medium">{lab.test_name}</td>
                  <td className="px-4 py-3 font-semibold text-slate-900">
                    {lab.numerical_value !== undefined && lab.numerical_value !== null
                      ? `${lab.numerical_value} ${lab.unit || ''}`
                      : lab.text_value || '--'}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">{lab.reference_range || '--'}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        lab.is_abnormal
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      {lab.is_abnormal ? 'Abnormal' : 'Normal'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};