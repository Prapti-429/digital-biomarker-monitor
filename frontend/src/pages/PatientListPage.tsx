/**
 * Patient Directory Roster Page Component.
 *
 * Provides clinical search, CML phase filtering, pagination, and patient navigation.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { clinicalService } from '../services/clinicalService';
import { Patient } from '../types/clinical';
import { PatientCard } from '../components/PatientCard';

export const PatientListPage: React.FC = () => {
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPhase, setSelectedPhase] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchPatients = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await clinicalService.searchPatients({
        q: searchQuery || undefined,
        disease_phase: selectedPhase || undefined,
        page,
        page_size: 12,
      });
      setPatients(response.items);
      setTotalPages(response.pages);
    } catch (err) {
      console.error('Failed to load patient roster:', err);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, selectedPhase, page]);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Patient Directory</h1>
          <p className="text-sm text-slate-500">
            Longitudinal CML Clinical Telemetry & Patient Cohorts
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          placeholder="Search by Patient Name, MRN, or Diagnosis..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setPage(1);
          }}
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
        />

        <select
          value={selectedPhase}
          onChange={(e) => {
            setSelectedPhase(e.target.value);
            setPage(1);
          }}
          className="px-4 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
        >
          <option value="">All CML Disease Phases</option>
          <option value="Chronic Phase">Chronic Phase</option>
          <option value="Accelerated Phase">Accelerated Phase</option>
          <option value="Blast Phase">Blast Phase</option>
        </select>
      </div>

      {/* Patient Grid */}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
        </div>
      ) : patients.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-slate-500">
          No patients found matching the search criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {patients.map((patient) => (
            <PatientCard
              key={patient.id}
              patient={patient}
              onSelect={(id) => navigate(`/patients/${id}`)}
            />
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 pt-4">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="px-4 py-2 text-sm font-medium bg-white border border-slate-300 rounded-lg disabled:opacity-50 hover:bg-slate-50"
          >
            Previous
          </button>
          <span className="text-sm text-slate-600">
            Page {page} of {totalPages}
          </span>
          <button
            disabled={page === totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            className="px-4 py-2 text-sm font-medium bg-white border border-slate-300 rounded-lg disabled:opacity-50 hover:bg-slate-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};