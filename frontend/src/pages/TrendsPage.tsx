import React, { useMemo, useState } from 'react';
import { TrendChart } from '../components/common/TrendChart';
import { InfoButton } from '../components/common/InfoButton';

interface Metric { name: string; current: number; min: number; max: number; unit: string; explanation: string; }

const metrics: Metric[] = [
  { name: 'Voice pattern', current: 82, min: 72, max: 88, unit: 'index', explanation: 'A combined view of simple voice measurements such as pitch, loudness and speaking activity. It shows how today compares with your own recent pattern.' },
  { name: 'Facial movement', current: 68, min: 55, max: 76, unit: 'index', explanation: 'How much visible facial movement the camera detected. Lighting and camera position can affect this estimate.' },
  { name: 'Eye / blink pattern', current: 74, min: 62, max: 81, unit: 'index', explanation: 'An estimate of changes around the eye area and blinking. It is not a clinical eye examination.' },
  { name: 'Movement pattern', current: 79, min: 70, max: 86, unit: 'index', explanation: 'A computer estimate of visible movement during the check-in. It is not a clinical gait test.' },
  { name: 'Breathing-related pattern', current: 71, min: 64, max: 80, unit: 'index', explanation: 'An estimate of rhythmic visible changes that may relate to breathing. It is not a medical breathing measurement.' },
  { name: 'Head movement', current: 77, min: 68, max: 84, unit: 'index', explanation: 'A measure of visible head-area movement and its variability during the camera sample.' },
];

function makeSeries(metric: Metric, count: number) {
  return Array.from({ length: count }, (_, i) => ({
    date: `D${i + 1}`,
    value: Math.round(metric.min + ((metric.current - metric.min) * (i + 1)) / count),
    baselineMin: metric.min,
    baselineMax: metric.max,
  }));
}

export const TrendsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [selected, setSelected] = useState(0);
  const metric = metrics[selected];
  const count = timeRange === '7d' ? 7 : timeRange === '30d' ? 10 : 12;
  const data = useMemo(() => makeSeries(metric, count), [metric, count]);
  const inside = metric.current >= metric.min && metric.current <= metric.max;

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">Data & Trends</h1>
          <p className="text-slate-400 text-sm mt-1">See today's measurements against your own usual pattern and how that pattern changes over time.</p>
        </div>
        <div className="flex rounded-xl bg-slate-900 border border-slate-800 p-1 self-start">
          {(['7d', '30d', '90d'] as const).map((r) => <button key={r} onClick={() => setTimeRange(r)} className={`px-3 py-1 text-xs font-medium rounded-lg ${timeRange === r ? 'bg-sky-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-slate-200'}`}>{r.toUpperCase()}</button>)}
        </div>
      </div>

      <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6">
        <div className="flex items-center gap-2"><h2 className="text-base font-bold text-white">Today compared with your usual pattern</h2><InfoButton title="How to read this">The shaded range is your personal usual range, learned from previous usable check-ins. The current value shows where today's measurement sits. This is not a universal medical ideal range.</InfoButton></div>
        <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-xl bg-slate-900 p-4"><div className="flex items-center gap-2 text-xs text-slate-400">Today <InfoButton title="Today">The latest available value for this measurement.</InfoButton></div><strong className="mt-1 block text-2xl text-white">{metric.current} <span className="text-xs text-slate-500">{metric.unit}</span></strong></div>
          <div className="rounded-xl bg-slate-900 p-4"><div className="flex items-center gap-2 text-xs text-slate-400">Your usual range <InfoButton title="Your usual range">This is based on your own earlier measurements when enough usable history is available. It is not a diagnosis or universal healthy range.</InfoButton></div><strong className="mt-1 block text-2xl text-white">{metric.min}–{metric.max}</strong></div>
          <div className="rounded-xl bg-slate-900 p-4"><div className="flex items-center gap-2 text-xs text-slate-400">Pattern <InfoButton title="Pattern">This tells you whether today's value sits inside or outside your own recent range. One unusual measurement does not by itself mean something is wrong.</InfoButton></div><strong className={`mt-1 block text-lg ${inside ? 'text-emerald-300' : 'text-amber-300'}`}>{inside ? 'Within your usual pattern' : 'Different from your usual pattern'}</strong></div>
        </div>
        <div className="mt-5 h-8 rounded-full bg-slate-900 border border-slate-800 overflow-hidden relative" aria-label="Current value compared with personal range">
          <div className="absolute inset-y-1 left-[25%] right-[15%] rounded-full bg-teal-500/20 border border-teal-400/20" title="Your usual range" />
          <div className="absolute inset-y-0 w-1 bg-sky-400" style={{ left: `${Math.min(98, Math.max(2, metric.current))}%` }} title="Today's value" />
        </div>
        <div className="mt-2 flex justify-between text-[10px] text-slate-500"><span>Lower</span><span>Your usual range</span><span>Higher</span></div>
      </section>

      <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8">
        <div className="flex items-center gap-2 mb-3"><h2 className="text-base font-bold text-white">Longitudinal graph</h2><InfoButton title="Longitudinal graph">Each point represents a recorded measurement. Looking across several check-ins is more useful than reacting to one point. The graph is for pattern monitoring, not diagnosis.</InfoButton></div>
        <div className="flex flex-wrap gap-2 mb-5">{metrics.map((item, i) => <button key={item.name} onClick={() => setSelected(i)} className={`rounded-lg border px-3 py-2 text-xs ${selected === i ? 'border-sky-400 bg-sky-500/10 text-sky-200' : 'border-slate-700 text-slate-400'}`}>{item.name}</button>)}</div>
        <TrendChart data={data} height={300} label={metric.name} metricUnit={metric.unit} />
        <p className="mt-4 text-xs leading-5 text-slate-500">{metric.explanation}</p>
      </section>

      <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6">
        <div className="flex items-center gap-2"><h2 className="text-base font-bold text-white">How the AI uses these data</h2><InfoButton title="AI assessment">NUVYRA checks data quality, compares usable measurements with your personal baseline, handles missing signals, looks for repeated changes and combines available modalities. The result is an observational research signal, not a medical diagnosis.</InfoButton></div>
        <div className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-3 text-sm">
          {['Data quality', 'Personal baseline', 'Change & persistence', 'Multimodal fusion'].map((label, i) => <div key={label} className="rounded-xl bg-slate-900 p-4"><span className="text-sky-300 font-semibold">{i + 1}.</span><p className="mt-1 text-white font-medium">{label}</p><p className="mt-1 text-xs leading-5 text-slate-500">{['Checks whether measurements are usable before interpreting them.', 'Compares you mainly with your own previous pattern.', 'Looks for repeated changes instead of overreacting to one result.', 'Combines available signals and clearly reports missing or weak modalities.'][i]}</p></div>)}
        </div>
      </section>
    </div>
  );
};