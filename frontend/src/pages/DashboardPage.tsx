import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { StatusBadge } from '../components/common/StatusBadge';
import { TrendChart } from '../components/common/TrendChart';
import { aiService, AIAnalysisResponse, AIHistoryResponse } from '../services/aiService';

const friendlyName = (raw: string) => {
  const key = raw.toLowerCase();
  if (key.includes('voice') || key.includes('acoustic') || key.includes('pitch') || key.includes('rms')) return 'Voice & speech';
  if (key.includes('face') || key.includes('facial')) return 'Facial movement';
  if (key.includes('blink') || key.includes('eye')) return 'Eyes & blinking';
  if (key.includes('gait') || key.includes('movement')) return 'Movement';
  if (key.includes('breath') || key.includes('resp')) return 'Breathing pattern';
  if (key.includes('head')) return 'Head movement';
  if (key.includes('survey') || key.includes('self')) return 'Self-report';
  return raw.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const explanationFor = (name: string) => {
  const key = name.toLowerCase();
  if (key.includes('voice') || key.includes('speech')) return 'Research-level speech features describe characteristics of how you speak. They are not a clinical speech assessment and are compared mainly with your own previous recordings.';
  if (key.includes('facial')) return 'Computer-vision features estimate natural facial movement. Lighting, camera position and image quality can affect these estimates. They are research proxies, not clinically validated measurements.';
  if (key.includes('eye') || key.includes('blink')) return 'The camera estimates blinking and eye-opening patterns. This is a research proxy, not an eye examination or clinically validated eye measurement.';
  if (key.includes('movement')) return 'Computer vision estimates visible movement patterns during your check-in. This is a research proxy and is not a clinical gait or mobility assessment.';
  if (key.includes('breath')) return 'The camera may estimate visible rhythmic changes related to breathing. This is a research proxy, not a respiratory test or clinical breathing measurement.';
  if (key.includes('head')) return 'Computer vision estimates visible changes in head position and movement. This is a research proxy and can be affected by camera position.';
  if (key.includes('self')) return 'This is information you reported about how you felt. It is kept separate from the objective signal estimates.';
  return 'This is one part of the research information NUVYRA uses to study your personal pattern over time.';
};

const Info: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative inline-block">
      <button type="button" aria-label={`Information about ${title}`} onClick={() => setOpen(v => !v)} className="w-6 h-6 rounded-full border border-slate-600 text-slate-300 text-xs hover:border-sky-400 hover:text-sky-300 transition">i</button>
      {open ? (
        <div className="absolute z-30 right-0 top-8 w-80 rounded-2xl border border-slate-700 bg-slate-950 p-4 shadow-2xl text-left">
          <div className="text-sm font-semibold text-white mb-1">{title}</div>
          <p className="text-xs leading-5 text-slate-300">{children}</p>
        </div>
      ) : null}
    </div>
  );
};

type FeatureCard = { name: string; value: string; deviation: number | null | undefined };

const FeatureCardView: React.FC<{ feature: FeatureCard }> = ({ feature }) => {
  const close = feature.deviation == null ? null : Math.abs(feature.deviation) <= 2;
  const label = close == null ? 'Information not available' : close ? 'Close to your usual' : 'Different from your usual';
  const labelClass = close === false ? 'text-amber-300' : 'text-emerald-300';
  const isProxy = /face|eye|movement|breath|head/i.test(feature.name);
  return (
    <div className="rounded-3xl bg-[#111827] border border-slate-800 p-5 hover:border-slate-700 transition">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-white">{feature.name}</h3>
          <p className="text-xs text-slate-500 mt-1">{label}</p>
        </div>
        <Info title={feature.name}>{explanationFor(feature.name)}</Info>
      </div>
      <div className="mt-5 flex items-end justify-between">
        <div>
          <div className="text-xs text-slate-500">Today's measurement</div>
          <div className="text-3xl font-bold text-white mt-1">{feature.value}</div>
        </div>
        <div className={`text-right text-xs font-medium ${labelClass}`}>{label}</div>
      </div>
      <div className="mt-5">
        <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
          <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-sky-500 to-teal-400" />
        </div>
        <div className="flex justify-between text-[10px] text-slate-600 mt-2"><span>Your lower range</span><span>Your usual range</span><span>Your higher range</span></div>
      </div>
      {isProxy ? <p className="mt-4 text-[10px] leading-4 text-slate-500">Research estimate · not a clinically validated measurement</p> : null}
    </div>
  );
};

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
    return points.length ? points : latest ? [{ date: 'Latest', value: Math.round(latest.overall_score) }] : [];
  }, [history, latest]);

  const featureCards: FeatureCard[] = latest?.features?.length
    ? latest.features.filter(feature => !/survey|self[_ -]?report/i.test(`${feature.category || ''} ${feature.name || ''}`)).slice(0, 6).map(feature => ({
        name: friendlyName(feature.category || feature.name),
        value: feature.value.toFixed(2),
        deviation: feature.deviation,
      }))
    : [
        { name: 'Voice & speech', value: '—', deviation: null },
        { name: 'Facial movement', value: '—', deviation: null },
        { name: 'Eyes & blinking', value: '—', deviation: null },
        { name: 'Movement', value: '—', deviation: null },
        { name: 'Breathing pattern', value: '—', deviation: null },
        { name: 'Head movement', value: '—', deviation: null },
      ];

  const statusLabel = !latest
    ? 'Waiting for your first check-in'
    : trend === 'IMPROVING'
      ? 'Moving closer to usual'
      : trend === 'DEGRADING'
        ? 'Some changes noticed'
        : 'Close to usual';

  return (
    <div className="space-y-8 pb-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-5">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-sky-400 font-semibold">Your NUVYRA space</p>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white mt-2">Your pattern today ✦</h1>
          <p className="text-slate-400 mt-2 max-w-2xl">A simple view of how today's research measurements compare with what is usual for you.</p>
        </div>
        <Link to="/check-in" className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-sky-500 to-teal-500 text-slate-950 font-semibold px-5 py-3 rounded-2xl text-sm">Today's check-in →</Link>
      </div>

      <div className="rounded-3xl bg-gradient-to-br from-sky-950/50 via-[#111b2d] to-[#0d1523] border border-sky-500/20 p-6 sm:p-8 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2"><h2 className="text-xl font-semibold text-white">How familiar is today?</h2><Info title="Your personal pattern">NUVYRA learns your usual pattern from previous check-ins. There is no single universal healthy number that applies to everyone.</Info></div>
            <p className="text-sm text-slate-400 mt-2">Your personal reference is more useful than a one-size-fits-all target.</p>
          </div>
          <StatusBadge status={latest ? status : 'stable'} label={statusLabel} />
        </div>

        <div className="mt-8 grid lg:grid-cols-3 gap-6 items-center">
          <div><div className="text-xs text-slate-500 uppercase tracking-wider">Experimental stability index</div><div className="text-6xl font-extrabold text-white mt-1">{latest ? Math.round(score) : '—'}</div><p className="text-xs text-slate-400 mt-2">A research index summarizing the available observations. It is not a medical score and has not been clinically validated.</p></div>
          <div className="lg:col-span-2 rounded-2xl bg-black/20 border border-white/5 p-5">
            <div className="flex justify-between text-xs mb-3"><span className="text-slate-400">Your usual pattern</span><span className="text-slate-400">Today</span></div>
            <div className="relative h-10 flex items-center"><div className="h-3 rounded-full bg-slate-700/80 w-full" /><div className="absolute left-[28%] right-[25%] h-5 rounded-full border border-sky-400/50 bg-sky-400/10" /><div className="absolute left-[62%] w-4 h-4 rounded-full bg-white shadow-lg" /></div>
            <div className="flex justify-between text-[11px] text-slate-500 mt-2"><span>Less like your usual</span><span>More like your usual</span></div>
            <p className="text-xs text-slate-300 mt-4">{latest ? "Today's combined research pattern is shown against your learned personal reference." : 'Complete a check-in to begin learning your personal reference.'}</p>
          </div>
        </div>
      </div>

      <section><div className="flex items-end justify-between mb-4"><div><h2 className="text-xl font-bold text-white">Your signals</h2><p className="text-sm text-slate-400 mt-1">Each card is one piece of your personal pattern.</p></div><Link to="/biomarkers" className="text-xs text-sky-400">Explore details →</Link></div><div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">{featureCards.map((feature, index) => <FeatureCardView key={`${feature.name}-${index}`} feature={feature} />)}</div></section>

      <div className="grid lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 rounded-3xl bg-[#111827] border border-slate-800 p-6"><div className="flex items-center justify-between"><div><h2 className="text-lg font-bold text-white">Your journey</h2><p className="text-xs text-slate-400 mt-1">See how your combined pattern changes over time.</p></div><Info title="Why trends matter">A single different day is not enough to establish a meaningful pattern. NUVYRA looks at repeated observations and their quality over time.</Info></div><div className="mt-5"><TrendChart data={trendData} label="Your pattern over time" /></div></div>
        <div className="rounded-3xl bg-[#111827] border border-slate-800 p-6"><div className="flex items-center gap-2"><h2 className="text-lg font-bold text-white">What NUVYRA noticed</h2><Info title="Explainable AI">The AI combines available signals, checks their quality, compares them with your personal history and explains the result. This is experimental research AI and has not been formally clinically validated.</Info></div><p className="text-sm text-slate-300 mt-4 leading-7">{latest?.explanation ?? 'Your first check-in will give NUVYRA the information it needs to start building your personal reference.'}</p><div className="mt-5 pt-4 border-t border-slate-800 space-y-2 text-xs"><div className="flex justify-between"><span className="text-slate-500">Information clarity</span><span className="text-slate-200">{latest ? `${Math.round(latest.confidence * 100)}%` : 'Not available yet'}</span></div><div className="flex justify-between"><span className="text-slate-500">Previous check-ins</span><span className="text-slate-200">{latest?.baseline_observations ?? history?.baseline_observations ?? 0}</span></div></div></div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5"><h3 className="text-sm font-semibold text-white">ⓘ How NUVYRA understands your data</h3><p className="text-xs leading-6 text-slate-400 mt-2">NUVYRA studies research-level digital-biomarker proxies from voice and computer vision. It checks data quality, learns your personal baseline, and looks for changes that persist over time. These signals can be affected by lighting, camera position, microphone quality, language, environment and ordinary day-to-day variation.</p></div>
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5"><h3 className="text-sm font-semibold text-white">🔒 Privacy & research use</h3><p className="text-xs leading-6 text-slate-400 mt-2">NUVYRA is designed as a privacy-sensitive research prototype. Authentication and backend protections are in place, but this project has not undergone a formal independent privacy or security audit. Do not use it as a substitute for a clinically regulated system.</p></div>
      <p className="text-[11px] text-slate-500 border-t border-slate-800 pt-4">NUVYRA is a research platform for longitudinal digital-biomarker exploration. Its computer-vision and speech features are research proxies, its stability index is experimental, and its AI explanations are exploratory. It does not diagnose disease or replace professional medical assessment.</p>
    </div>
  );
};
