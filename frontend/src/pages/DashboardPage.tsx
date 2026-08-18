import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { StatusBadge } from '../components/common/StatusBadge';
import { Sparkline } from '../components/common/Sparkline';
import { TrendChart } from '../components/common/TrendChart';
import { aiService, AIAnalysisResponse, AIHistoryResponse } from '../services/aiService';

export const DashboardPage: React.FC = () => {
  const [latest, setLatest] = useState<AIAnalysisResponse | null>(null);
  const [history, setHistory] = useState<AIHistoryResponse | null>(null);

  useEffect(() => {
    let active = true;
    Promise.allSettled([aiService.latest(), aiService.history(30)]).then(([latestResult, historyResult]) => {
      if (!active) return;
      if (latestResult.status === 'fulfilled') setLatest(latestResult.value);
      if (historyResult.status === 'fulfilled') setHistory(historyResult.value);
    });
    return () => { active = false; };
  }, []);

  const score = latest?.overall_score ?? 0;
  const trend = latest?.trend ?? 'INITIAL';
  const status = score >= 80 ? 'stable' : score >= 60 ? 'improving' : 'degrading';
  const trendData = useMemo(() => {
    const points = history?.items?.map((item, index) => ({
      date: new Date(item.generated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      value: Math.round(item.score),
      label: `Observation ${index + 1}`,
    })) ?? [];
    return points.length ? points : (latest ? [{ date: 'Latest', value: Math.round(latest.overall_score) }] : []);
  }, [history, latest]);

  const featureCards = latest?.features?.length
    ? latest.features.slice(0, 4).map((feature) => ({
        category: feature.category.replace(/_/g, ' ').toUpperCase(),
        value: feature.value.toFixed(2),
        unit: '',
        status: feature.deviation !== null && feature.deviation !== undefined && feature.deviation > 2 ? 'degrading' : 'stable',
        detail: feature.name.replace(/_/g, ' '),
      }))
    : [
        { category: 'VOICE PATTERNS', value: '—', unit: '', status: 'stable', detail: 'Complete a check-in to populate acoustic features' },
        { category: 'FACIAL DYNAMICS', value: '—', unit: '', status: 'stable', detail: 'Complete a check-in to populate motion features' },
        { category: 'SURVEY SIGNALS', value: '—', unit: '', status: 'stable', detail: 'Complete a check-in to populate personal baseline' },
        { category: 'AI STABILITY', value: latest ? String(Math.round(score)) : '—', unit: latest ? '/100' : '', status, detail: 'Personalized longitudinal score' },
      ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">Your monitoring dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">Longitudinal observations are compared against your personal baseline.</p>
        </div>
        <Link to="/check-in" className="inline-flex items-center gap-2 bg-gradient-to-r from-sky-500 to-teal-500 text-slate-950 font-semibold px-4 py-2.5 rounded-xl text-sm">Daily check-in →</Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 rounded-2xl bg-gradient-to-b from-[#162032] to-[#0F1726] border border-slate-800 p-6 sm:p-8 shadow-xl">
          <div className="flex items-start justify-between"><div><span className="text-xs uppercase tracking-wider font-mono text-sky-400 font-semibold">NUVYRA HEALTH STABILITY INDEX</span><h2 className="text-lg font-medium text-slate-200 mt-1">Personalized longitudinal trajectory</h2></div><StatusBadge status={latest ? status : 'stable'} label={latest ? trend : 'Awaiting first AI observation'} /></div>
          <div className="my-6 grid grid-cols-1 sm:grid-cols-2 gap-6 items-center">
            <div><div className="flex items-baseline space-x-2"><span className="text-6xl font-extrabold text-white">{latest ? Math.round(score) : '—'}</span>{latest && <span className="text-slate-400 text-sm">/ 100</span>}</div><p className="text-xs text-slate-400 mt-2">Observational score generated from available multimodal signals.</p></div>
            <div className="border-t sm:border-t-0 sm:border-l border-slate-800 sm:pl-6 space-y-2 text-xs"><div className="flex justify-between text-slate-400"><span>Model confidence</span><span className="text-slate-200 font-mono">{latest ? `${Math.round(latest.confidence * 100)}%` : '—'}</span></div><div className="flex justify-between text-slate-400"><span>Baseline observations</span><span className="text-slate-200">{latest?.baseline_observations ?? history?.baseline_observations ?? 0}</span></div><div className="flex justify-between text-slate-400"><span>Model</span><span className="text-slate-200">{latest?.model_version ?? history?.model_version ?? '—'}</span></div></div>
          </div>
          <div className="pt-4 border-t border-slate-800/80"><TrendChart data={trendData} label="Observed stability trajectory" /></div>
        </div>

        <div className="flex flex-col gap-6">
          <div className="rounded-2xl bg-gradient-to-br from-sky-950/40 via-[#131C2D] to-[#0E1624] border border-sky-500/20 p-6"><div className="text-xs text-sky-400 font-mono">TODAY'S PROTOCOL</div><h3 className="text-lg font-bold text-white mt-2">Daily check-in</h3><p className="text-xs text-slate-300 mt-1 leading-relaxed">Capture survey, acoustic and facial-motion signals, then run the personalized inference model.</p><Link to="/check-in" className="mt-6 w-full flex items-center justify-center bg-sky-500 text-slate-950 font-semibold py-2.5 rounded-xl text-xs">Start check-in</Link></div>
          <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6"><h4 className="text-xs font-mono text-slate-400 uppercase tracking-wider">Latest AI interpretation</h4><p className="text-xs text-slate-400 mt-4 leading-relaxed">{latest?.explanation ?? 'No AI analysis yet. Complete your first daily check-in to establish a personal baseline.'}</p></div>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-4"><div><h3 className="text-lg font-bold text-white">Multimodal biomarker streams</h3><p className="text-xs text-slate-400">Features collected during your latest analysis</p></div><Link to="/biomarkers" className="text-xs text-sky-400">View detailed channels →</Link></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {featureCards.map((feature, index) => <div key={`${feature.category}-${index}`} className="rounded-xl bg-[#111827] border border-slate-800 p-5 flex flex-col justify-between"><div><div className="flex items-center justify-between"><span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">{feature.category}</span><StatusBadge status={feature.status} size="sm" /></div><div className="mt-3 flex items-baseline space-x-2"><span className="text-3xl font-bold text-white">{feature.value}</span><span className="text-xs text-slate-500">{feature.unit}</span></div><p className="text-xs text-slate-400 mt-2 leading-relaxed">{feature.detail}</p></div><div className="mt-4 pt-3 border-t border-slate-800/80"><Sparkline data={latest ? [Math.max(0, Math.round(score) - 6), Math.max(0, Math.round(score) - 3), Math.round(score)] : [0]} width={100} height={28} /></div></div>)}
        </div>
      </div>

      <p className="text-[11px] text-slate-500 border-t border-slate-800 pt-4">NUVYRA AI produces observational digital-biomarker signals for longitudinal monitoring. It is not a diagnosis and should not replace professional medical assessment.</p>
    </div>
  );
};
