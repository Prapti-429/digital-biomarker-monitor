import React from 'react';
import { Link } from 'react-router-dom';
import { StatusBadge } from '../components/common/StatusBadge';
import { Sparkline } from '../components/common/Sparkline';
import { TrendChart } from '../components/common/TrendChart';

export const DashboardPage: React.FC = () => {
  const trendData = [
    { date: 'Oct 10', value: 80 },
    { date: 'Oct 12', value: 82 },
    { date: 'Oct 14', value: 79 },
    { date: 'Oct 16', value: 81 },
    { date: 'Oct 18', value: 83 },
    { date: 'Oct 20', value: 82 },
    { date: 'Today', value: 84 },
  ];

  const biomarkers = [
    {
      category: 'VOICE PATTERNS',
      value: '78',
      unit: '/100',
      status: 'stable',
      trend: '+1.2%',
      sparkline: [74, 75, 76, 75, 77, 78],
      detail: 'Speech tempo: 3.8 syll/s within baseline range'
    },
    {
      category: 'FACIAL DYNAMICS',
      value: '84',
      unit: '/100',
      status: 'stable',
      trend: 'Optimal',
      sparkline: [82, 83, 84, 83, 85, 84],
      detail: 'Blink frequency & facial asymmetry stable'
    },
    {
      category: 'MOVEMENT & GAIT',
      value: '81',
      unit: '/100',
      status: 'improving',
      trend: '+3.4%',
      sparkline: [72, 75, 76, 78, 80, 81],
      detail: 'Kinematic acceleration stability elevated'
    },
    {
      category: 'REPORTED SYMPTOMS',
      value: '88',
      unit: '/100',
      status: 'stable',
      trend: 'Consistent',
      sparkline: [88, 88, 86, 88, 88, 88],
      detail: 'Fatigue severity 1/10; mood positive'
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            Good morning, Alex
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Your longitudinal health signals are continuous and aligned with your personal baseline.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/check-in"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 text-slate-950 font-semibold px-4 py-2.5 rounded-xl text-sm transition-all shadow-md hover:shadow-sky-500/20"
          >
            <span>Daily check-in</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </Link>
        </div>
      </div>

      {/* Primary Stability Hero Card & Quick Check-in Banner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stability Index Hero */}
        <div className="lg:col-span-2 rounded-2xl bg-gradient-to-b from-[#162032] to-[#0F1726] border border-slate-800 p-6 sm:p-8 flex flex-col justify-between shadow-xl">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-xs uppercase tracking-wider font-mono text-sky-400 font-semibold">
                NUVYRA HEALTH STABILITY INDEX
              </span>
              <h2 className="text-lg font-medium text-slate-200 mt-1">Longitudinal Trajectory</h2>
            </div>
            <StatusBadge status="stable" label="Within Personal Baseline" />
          </div>

          <div className="my-6 grid grid-cols-1 sm:grid-cols-2 gap-6 items-center">
            <div>
              <div className="flex items-baseline space-x-2">
                <span className="text-6xl font-extrabold text-white tracking-tight">84</span>
                <span className="text-slate-400 text-sm font-medium">/ 100</span>
              </div>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Calculated across 4 multimodal channels over the last 30 observational days.
              </p>
            </div>
            <div className="border-t sm:border-t-0 sm:border-l border-slate-800 sm:pl-6 space-y-2">
              <div className="text-xs flex justify-between text-slate-400">
                <span>Confidence interval</span>
                <span className="text-slate-200 font-mono">81 – 87</span>
              </div>
              <div className="text-xs flex justify-between text-slate-400">
                <span>Signal variation</span>
                <span className="text-emerald-400 font-medium">Low (±1.4%)</span>
              </div>
              <div className="text-xs flex justify-between text-slate-400">
                <span>Observation phase</span>
                <span className="text-slate-200">Day 42 of Cohort</span>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/80">
            <TrendChart data={trendData} label="30-Day Stability Trajectory" />
          </div>
        </div>

        {/* Daily Check-in Action Card & Protocol Status */}
        <div className="flex flex-col gap-6">
          <div className="rounded-2xl bg-gradient-to-br from-sky-950/40 via-[#131C2D] to-[#0E1624] border border-sky-500/20 p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between text-xs text-sky-400 font-mono">
                <span>TODAY'S PROTOCOL</span>
                <span>PROGRESS: 1 / 3</span>
              </div>
              <h3 className="text-lg font-bold text-white mt-2">Daily Check-in</h3>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                Record 30 seconds of speech and motor movements to keep your baseline continuous.
              </p>

              <div className="w-full bg-slate-800/80 h-1.5 rounded-full mt-4 overflow-hidden">
                <div className="bg-gradient-to-r from-sky-400 to-teal-400 h-full w-1/3 rounded-full" />
              </div>
            </div>

            <div className="mt-6 space-y-2">
              <Link
                to="/check-in"
                className="w-full flex items-center justify-center gap-2 bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold py-2.5 rounded-xl text-xs transition-colors"
              >
                Continue Check-in
              </Link>
              <p className="text-[10px] text-center text-slate-500">
                Estimated time remaining: 2 minutes
              </p>
            </div>
          </div>

          {/* Contributing Signal Breakdown Card */}
          <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 flex-1 flex flex-col justify-between">
            <h4 className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              Signal Contributors
            </h4>
            <div className="space-y-3 mt-4">
              {[
                { name: 'Vocal acoustic density', state: 'Normal', color: 'bg-emerald-400' },
                { name: 'Facial micro-symmetry', state: 'Normal', color: 'bg-emerald-400' },
                { name: 'Tremor & motor speed', state: 'Elevated baseline', color: 'bg-teal-400' },
              ].map((s, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${s.color}`} />
                    <span className="text-slate-300">{s.name}</span>
                  </div>
                  <span className="text-slate-500 font-mono text-[11px]">{s.state}</span>
                </div>
              ))}
            </div>
            <p className="text-[11px] text-slate-500 mt-4 pt-3 border-t border-slate-800">
              Interpreted via personal baseline deviation algorithms.
            </p>
          </div>
        </div>
      </div>

      {/* Multimodal Biomarker Channels */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-white">Multimodal Biomarker Streams</h3>
            <p className="text-xs text-slate-400">Current observations compared against your personal baseline</p>
          </div>
          <Link to="/biomarkers" className="text-xs text-sky-400 hover:text-sky-300 font-medium">
            View detailed channels &rarr;
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {biomarkers.map((b, idx) => (
            <div
              key={idx}
              className="rounded-xl bg-[#111827] border border-slate-800 p-5 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
                    {b.category}
                  </span>
                  <StatusBadge status={b.status} size="sm" />
                </div>
                <div className="mt-3 flex items-baseline space-x-2">
                  <span className="text-3xl font-bold text-white">{b.value}</span>
                  <span className="text-xs text-slate-500">{b.unit}</span>
                </div>
                <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                  {b.detail}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                <Sparkline data={b.sparkline} width={100} height={28} />
                <span className="text-xs font-mono text-emerald-400">{b.trend}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};