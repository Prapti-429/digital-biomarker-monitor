import React, { useEffect, useMemo, useState } from 'react';
import { InfoButton } from '../components/common/InfoButton';
import { aiService, AIHistoryPoint } from '../services/aiService';

type TimelineEvent = { id: string; date: string; title: string; desc: string };

const formatDateTime = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Date unavailable';
  return date.toLocaleString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
};

export const TimelinePage: React.FC = () => {
  const [history, setHistory] = useState<AIHistoryPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    aiService.history(90)
      .then((response) => {
        if (!active) return;
        setHistory((response?.items || []).filter((item) => item?.generated_at && !Number.isNaN(new Date(item.generated_at).getTime())));
      })
      .catch((err: any) => active && setError(err?.message || 'Unable to load your saved timeline right now.'))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  const events = useMemo<TimelineEvent[]>(() => [...history]
    .sort((a, b) => new Date(b.generated_at).getTime() - new Date(a.generated_at).getTime())
    .map((item) => ({
      id: item.check_in_id,
      date: formatDateTime(item.generated_at),
      title: 'Daily check-in completed',
      desc: `NUVYRA saved this multimodal assessment with a ${Number(item.score).toFixed(1)}/100 pattern score and ${Math.round(Number(item.confidence || 0) * 100)}% data confidence.`,
    })), [history]);

  return (
    <div className="space-y-8 max-w-4xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">Your timeline</h1>
          <p className="text-slate-400 text-sm mt-1">A chronological record based only on your saved NUVYRA check-ins.</p>
        </div>
        <InfoButton title="About your timeline">The date and time come directly from your saved AI assessment. NUVYRA does not invent historical events or show placeholder dates.</InfoButton>
      </div>

      {error && <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">{error}</div>}

      {loading ? <div className="rounded-2xl bg-[#111827] border border-slate-800 p-10 text-center text-sm text-slate-400">Loading your saved timeline…</div> : events.length === 0 ? (
        <div className="rounded-2xl bg-[#111827] border border-slate-800 p-10 text-center">
          <p className="text-white font-semibold">Your timeline will start here.</p>
          <p className="text-slate-400 text-sm mt-2">Complete and save a daily check-in to create your first entry.</p>
        </div>
      ) : (
        <div className="relative pl-6 border-l border-slate-800 space-y-6">
          {events.map((event) => <div key={event.id} className="relative group">
            <div className="absolute -left-[31px] top-1.5 w-3 h-3 rounded-full bg-[#0B0F17] border-2 border-sky-400 group-hover:scale-125 transition-transform" />
            <span className="text-xs text-slate-500">{event.date}</span>
            <div className="mt-2 rounded-xl bg-[#111827] border border-slate-800 p-5 hover:border-slate-700 transition-all">
              <div className="flex items-center justify-between gap-3"><h3 className="text-sm font-semibold text-white">{event.title}</h3><span className="rounded-full bg-sky-500/10 px-2 py-1 text-[10px] font-semibold text-sky-300">Saved</span></div>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">{event.desc}</p>
            </div>
          </div>)}
        </div>
      )}
    </div>
  );
};

export default TimelinePage;
