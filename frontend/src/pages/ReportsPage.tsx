import React, { useEffect, useMemo, useState } from 'react';
import { aiService, AIHistoryPoint } from '../services/aiService';

type ReportDefinition = {
  title: string;
  description: string;
  fileName: string;
  days: number;
};

const reports: ReportDefinition[] = [
  { title: 'Weekly Longitudinal Summary', description: 'Your most recent 7 days of saved NUVYRA observations.', fileName: 'nuvyra-weekly-longitudinal-report.csv', days: 7 },
  { title: 'Monthly Multimodal Synthesis', description: 'Your most recent 30 days of saved multimodal observations.', fileName: 'nuvyra-monthly-multimodal-report.csv', days: 30 },
  { title: 'Baseline Calibration Benchmark', description: 'A structured export of up to 90 days for baseline and trajectory review.', fileName: 'nuvyra-baseline-trajectory-report.csv', days: 90 },
];

const csvCell = (value: unknown) => {
  const text = value == null ? '' : String(value);
  return `"${text.replace(/"/g, '""')}"`;
};

const buildCsv = (title: string, points: AIHistoryPoint[]) => {
  const rows = [
    ['NUVYRA Longitudinal Report', title],
    ['Generated', new Date().toISOString()],
    ['Notice', 'Research and observational summary only; not a diagnosis or medical report.'],
    [],
    ['Check-in ID', 'Generated at', 'Pattern score', 'Confidence'],
    ...points.map((item) => [
      item.check_in_id,
      item.generated_at,
      Number(item.score).toFixed(2),
      Number(item.confidence || 0).toFixed(4),
    ]),
  ];
  return rows.map((row) => row.map(csvCell).join(',')).join('\r\n');
};

export const ReportsPage: React.FC = () => {
  const [history, setHistory] = useState<AIHistoryPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    aiService.history(90)
      .then((response) => {
        if (active) setHistory(response?.items || []);
      })
      .catch((err: any) => {
        if (active) setError(err?.message || 'Unable to load your saved report data.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  const sortedHistory = useMemo(
    () => [...history].sort((a, b) => new Date(a.generated_at).getTime() - new Date(b.generated_at).getTime()),
    [history],
  );

  const downloadReport = (report: ReportDefinition) => {
    setDownloading(report.title);
    try {
      const points = sortedHistory.slice(-report.days);
      if (!points.length) throw new Error('No saved check-ins are available for this report yet.');

      const csv = buildCsv(report.title, points);
      const blob = new Blob(['\uFEFF', csv], { type: 'text/csv;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = report.fileName;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setError(null);
    } catch (err: any) {
      setError(err?.message || 'The report could not be downloaded.');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">Longitudinal Reports</h1>
        <p className="text-slate-400 text-sm mt-1">
          Export structured summaries of your baseline trajectory for research and observational review.
        </p>
      </div>

      {error && <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">{error}</div>}

      <div className="space-y-4">
        {reports.map((report) => {
          const available = Math.min(report.days, sortedHistory.length);
          return (
            <div key={report.title} className="rounded-2xl bg-[#111827] border border-slate-800 p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-slate-700 transition-all">
              <div>
                <h3 className="text-sm font-semibold text-white">{report.title}</h3>
                <p className="text-xs text-slate-400 mt-1">{report.description}</p>
                <p className="text-[11px] text-slate-500 mt-2">
                  {loading ? 'Loading saved observations…' : `${available} saved observation${available === 1 ? '' : 's'} available · CSV`}
                </p>
              </div>
              <button
                type="button"
                onClick={() => downloadReport(report)}
                disabled={loading || downloading === report.title || available === 0}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {downloading === report.title ? 'Preparing…' : 'Download Report'}
              </button>
            </div>
          );
        })}
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4 text-xs leading-5 text-slate-400">
        Downloads contain only your saved NUVYRA longitudinal observations. They are research/observational summaries and are not diagnostic medical reports.
      </div>
    </div>
  );
};

export default ReportsPage;
