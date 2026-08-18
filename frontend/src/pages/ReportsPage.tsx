import React from 'react';

export const ReportsPage: React.FC = () => {
  const reports = [
    { title: 'Weekly Longitudinal Summary', date: 'Oct 14 – Oct 21, 2026', size: '1.4 MB PDF' },
    { title: 'Monthly Multimodal Synthesis', date: 'September 2026', size: '3.1 MB PDF' },
    { title: 'Baseline Calibration Benchmark', date: 'Initial Onboarding', size: '0.8 MB PDF' },
  ];

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Longitudinal Reports
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Export structured summaries of your baseline trajectory for research and observational review.
        </p>
      </div>

      <div className="space-y-4">
        {reports.map((rep, i) => (
          <div key={i} className="rounded-2xl bg-[#111827] border border-slate-800 p-5 flex items-center justify-between hover:border-slate-700 transition-all">
            <div>
              <h3 className="text-sm font-semibold text-white">{rep.title}</h3>
              <p className="text-xs text-slate-500 mt-0.5">{rep.date} &bull; {rep.size}</p>
            </div>
            <button className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all">
              Download Report
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};