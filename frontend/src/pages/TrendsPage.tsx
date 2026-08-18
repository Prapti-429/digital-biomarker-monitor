import React, { useState } from 'react';
import { TrendChart } from '../components/common/TrendChart';

export const TrendsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  const sampleTrend = [
    { date: 'W1', value: 79 },
    { date: 'W2', value: 81 },
    { date: 'W3', value: 80 },
    { date: 'W4', value: 84 },
    { date: 'W5', value: 83 },
    { date: 'W6', value: 84 },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            Longitudinal Signal Trends
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Analyzing longitudinal drift and steady-state patterns over extended time horizons.
          </p>
        </div>

        {/* Time range switcher */}
        <div className="flex rounded-xl bg-slate-900 border border-slate-800 p-1 self-start">
          {(['7d', '30d', '90d'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setTimeRange(r)}
              className={`px-3 py-1 text-xs font-medium rounded-lg transition-all ${
                timeRange === r
                  ? 'bg-sky-500 text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {r.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Main Chart Visualization */}
      <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8">
        <TrendChart data={sampleTrend} height={300} label="Multimodal Composite Trajectory" />
      </div>

      {/* Interpretability Section: What's Changed? */}
      <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6">
        <h2 className="text-base font-bold text-white">What's changed in your baseline?</h2>
        <p className="text-xs text-slate-400 mt-1">
          Algorithmic breakdown of contributing biometric signals over the selected period.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-4">
            <span className="text-[11px] font-mono uppercase text-teal-400 font-semibold">Voice Stability</span>
            <p className="text-sm font-semibold text-white mt-1">Steady Cadence</p>
            <p className="text-xs text-slate-400 mt-1">Speech rhythm has maintained 98% concordance with your 60-day baseline.</p>
          </div>
          <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-4">
            <span className="text-[11px] font-mono uppercase text-sky-400 font-semibold">Motor Velocity</span>
            <p className="text-sm font-semibold text-white mt-1">+4% Speed Shift</p>
            <p className="text-xs text-slate-400 mt-1">Finger-tapping frequency showed subtle improvement in rotational consistency.</p>
          </div>
          <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-4">
            <span className="text-[11px] font-mono uppercase text-emerald-400 font-semibold">Reported Symptoms</span>
            <p className="text-sm font-semibold text-white mt-1">No Drift Observed</p>
            <p className="text-xs text-slate-400 mt-1">Energy and mood metrics have remained inside the personal normal range.</p>
          </div>
        </div>
      </div>
    </div>
  );
};