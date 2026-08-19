import React, { useEffect, useMemo, useState } from 'react';
import { TrendChart } from '../components/common/TrendChart';
import { InfoButton } from '../components/common/InfoButton';
import { aiService, AIHistoryPoint } from '../services/aiService';

function personalRange(values: number[]) {
  if (values.length < 5) return null;
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const sd = Math.sqrt(values.reduce((a, b) => a + (b - mean) ** 2, 0) / values.length);
  return { min: Math.max(0, Math.round(mean - 1.5 * sd)), max: Math.min(100, Math.round(mean + 1.5 * sd)) };
}

export const TrendsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [history, setHistory] = useState<AIHistoryPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    aiService.history(90).then((response) => { if (active) setHistory(response.items || []); }).catch((err: any) => { if (active) setError(err?.message || 'Unable to load your longitudinal data.'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const visible = useMemo(() => history.slice(-(timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90)), [history, timeRange]);
  const values = visible.map(point => point.score);
  const range = personalRange(values);
  const latest = visible[visible.length - 1];
  const chartData = visible.map(point => ({ date: new Date(point.generated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }), value: Number(point.score.toFixed(1)), baselineMin: range?.min, baselineMax: range?.max }));
  const inRange = latest && range ? latest.score >= range.min && latest.score <= range.max : null;

  return <div className="space-y-8">
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"><div><h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">Data & Trends</h1><p className="text-slate-400 text-sm mt-1">Your real NUVYRA AI check-ins, shown graphically against your own recent pattern.</p></div><div className="flex rounded-xl bg-slate-900 border border-slate-800 p-1 self-start">{(['7d','30d','90d'] as const).map(r => <button key={r} onClick={() => setTimeRange(r)} className={`px-3 py-1 text-xs font-medium rounded-lg ${timeRange === r ? 'bg-sky-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-slate-200'}`}>{r.toUpperCase()}</button>)}</div></div>
    {error && <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">{error}</div>}
    {loading ? <div className="rounded-2xl bg-[#111827] border border-slate-800 p-10 text-center text-sm text-slate-400">Loading your longitudinal data…</div> : <>
      <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6"><div className="flex items-center gap-2"><h2 className="text-base font-bold text-white">Today vs your usual pattern</h2><InfoButton title="How to read this">The usual range is calculated from your own recent saved AI scores when enough history exists. It is not a universal medical ideal or diagnosis.</InfoButton></div>
        {latest ? <div className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="rounded-xl bg-slate-900 p-4"><div className="flex items-center gap-2 text-xs text-slate-400">Today <InfoButton title="Today's score">The latest composite score returned by the NUVYRA AI pipeline for this check-in.</InfoButton></div><strong className="mt-1 block text-2xl text-white">{latest.score.toFixed(1)}</strong></div>
          <div className="rounded-xl bg-slate-900 p-4"><div className="flex items-center gap-2 text-xs text-slate-400">Your usual range <InfoButton title="Your usual range">This is estimated from your own previous scores after enough usable history has been collected.</InfoButton></div><strong className="mt-1 block text-2xl text-white">{range ? `${range.min}–${range.max}` : 'Building'}</strong></div>
          <div className="rounded-xl bg-slate-900 p-4"><div className="flex items-center gap-2 text-xs text-slate-400">Pattern <InfoButton title="Pattern">One unusual result does not prove that something is wrong. Repeated changes are more meaningful.</InfoButton></div><strong className={`mt-1 block text-lg ${inRange === null ? 'text-slate-300' : inRange ? 'text-emerald-300' : 'text-amber-300'}`}>{inRange === null ? 'Need more history' : inRange ? 'Within your usual pattern' : 'Different from your usual pattern'}</strong></div>
          <div className="rounded-xl bg-slate-900 p-4"><div className="flex items-center gap-2 text-xs text-slate-400">Confidence <InfoButton title="Confidence">Confidence tells you how much usable information the AI had for the latest check-in. Lower confidence means more caution is needed.</InfoButton></div><strong className="mt-1 block text-lg text-white">{Math.round(latest.confidence * 100)}%</strong></div>
        </div> : <p className="mt-5 text-sm text-slate-400">No completed AI check-ins are available yet. Complete a daily check-in to begin your personal baseline.</p>}
      </section>
      <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8"><div className="flex items-center gap-2 mb-3"><h2 className="text-base font-bold text-white">Longitudinal graph</h2><InfoButton title="Longitudinal graph">Every point here comes from your actual saved AI check-in history. When enough history exists, the shaded range represents your own recent pattern.</InfoButton></div>{chartData.length ? <TrendChart data={chartData} height={300} label="Multimodal AI composite trajectory" metricUnit="score" /> : <div className="h-60 flex items-center justify-center rounded-xl bg-slate-900/40 border border-slate-800 text-sm text-slate-400">No longitudinal trend data recorded yet.</div>}<p className="mt-4 text-xs leading-5 text-slate-500">This graph monitors recorded patterns. It does not establish a medical ideal or diagnose a condition.</p></section>
      {latest && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6"><div className="flex items-center gap-2"><h2 className="text-base font-bold text-white">How the AI assesses your data</h2><InfoButton title="AI assessment">NUVYRA checks data quality, compares usable measurements with your personal baseline, handles missing signals, looks for repeated changes and combines available modalities. It produces an observational research signal, not a diagnosis.</InfoButton></div><div className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-3">{[['Data quality','Checks whether measurements are usable before interpretation.'],['Personal baseline','Compares you mainly with your own previous pattern.'],['Change & persistence','Looks for repeated changes instead of overreacting to one result.'],['Multimodal fusion','Combines available signals and reports missing or weak modalities.']].map(([title,text],i) => <div key={title} className="rounded-xl bg-slate-900 p-4"><span className="text-sky-300 font-semibold">{i+1}.</span><p className="mt-1 text-white font-medium">{title}</p><p className="mt-1 text-xs leading-5 text-slate-500">{text}</p></div>)}</div></section>}
    </>}
  </div>;
};