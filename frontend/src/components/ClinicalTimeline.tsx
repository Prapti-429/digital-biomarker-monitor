import React, { useEffect, useState, useCallback } from 'react';
import { apiClient } from '../services/apiClient';

export interface TimelineEventItem {
  event_id: string;
  event_type: 'VITAL_SIGNS' | 'LAB_RESULT' | 'SYMPTOM' | 'MEDICATION' | 'NUTRITION' | 'FILE_UPLOAD';
  timestamp: string;
  title: string;
  subtitle?: string;
  severity_indicator: 'normal' | 'warning' | 'alert' | 'info';
  details: Record<string, unknown>;
}

export interface ClinicalTimelineProps {
  patientId: string;
}

export const ClinicalTimeline: React.FC<ClinicalTimelineProps> = ({ patientId }) => {
  const [events, setEvents] = useState<TimelineEventItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL');

  const fetchTimeline = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params: Record<string, unknown> = { page: 1, page_size: 50 };
      if (selectedFilter !== 'ALL') {
        params.event_types = [selectedFilter];
      }

      const response = await apiClient.get(`/clinical/timeline/patient/${patientId}`, { params });
      setEvents(response.data.events || []);
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'message' in err 
        ? String(err.message) 
        : 'Failed to load timeline telemetry.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [patientId, selectedFilter]);

  useEffect(() => {
    fetchTimeline();
  }, [fetchTimeline]);

  const getBadgeColor = (severity: TimelineEventItem['severity_indicator']) => {
    switch (severity) {
      case 'alert':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      case 'warning':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'info':
        return 'bg-sky-100 text-sky-800 border-sky-300';
      case 'normal':
      default:
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-100 mb-6 gap-4">
        <div>
          <h3 className="text-lg font-bold text-slate-900">Longitudinal Clinical Master Timeline</h3>
          <p className="text-xs text-slate-500 mt-1">Unified chronological event telemetry stream</p>
        </div>

        <div className="flex items-center space-x-2">
          {['ALL', 'VITAL_SIGNS', 'LAB_RESULT', 'SYMPTOM', 'MEDICATION', 'FILE_UPLOAD'].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedFilter(type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                selectedFilter === type
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {type === 'ALL' ? 'All Events' : type.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : error ? (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={fetchTimeline} className="text-xs font-bold underline">Retry</button>
        </div>
      ) : events.length === 0 ? (
        <div className="text-center py-12 text-slate-400 text-sm">
          No recorded clinical events found for this patient filter.
        </div>
      ) : (
        <div className="relative border-l-2 border-indigo-100 ml-4 space-y-6">
          {events.map((evt) => (
            <div key={evt.event_id} className="mb-6 ml-6 group relative">
              {/* Timeline Bullet Point */}
              <span className="absolute -left-[31px] top-1.5 h-3.5 w-3.5 rounded-full border-2 border-white bg-indigo-600 shadow-sm group-hover:scale-125 transition-transform"></span>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 hover:border-indigo-300 transition-colors">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
                    {evt.event_type.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-slate-400">
                    {new Date(evt.timestamp).toLocaleString()}
                  </span>
                </div>

                <div className="flex items-start justify-between">
                  <h4 className="text-sm font-semibold text-slate-800">{evt.title}</h4>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${getBadgeColor(evt.severity_indicator)}`}>
                    {evt.severity_indicator}
                  </span>
                </div>

                {evt.subtitle && (
                  <p className="text-xs text-slate-600 mt-1 font-medium">{evt.subtitle}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};