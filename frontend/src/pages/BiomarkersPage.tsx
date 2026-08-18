import React, { useState } from 'react';
import { StatusBadge, StatusVariant } from '../components/common/StatusBadge';
import { Sparkline } from '../components/common/Sparkline';

type ChannelType = 'all' | 'voice' | 'face' | 'motor' | 'symptoms';

interface BiomarkerMetric {
  channel: 'voice' | 'face' | 'motor' | 'symptoms';
  name: string;
  current: string;
  baseline: string;
  status: StatusVariant;
  trend: string;
  description: string;
  sparkline: number[];
}

export const BiomarkersPage: React.FC = () => {
  const [selectedChannel, setSelectedChannel] = useState<ChannelType>('all');

  const biomarkerMetrics: BiomarkerMetric[] = [
    {
      channel: 'voice',
      name: 'Speech Articulation Rate',
      current: '3.8 syll/sec',
      baseline: '3.6 – 4.1 syll/sec',
      status: 'stable',
      trend: 'Within baseline',
      description: 'Derived from daily phonation samples. Measures syllable frequency and pause distribution.',
      sparkline: [3.7, 3.8, 3.7, 3.9, 3.8]
    },
    {
      channel: 'voice',
      name: 'Vocal Jitter & Shimmer',
      current: '1.2%',
      baseline: '1.0% – 1.5%',
      status: 'stable',
      trend: 'Within baseline',
      description: 'Micro-fluctuations in fundamental frequency and amplitude during sustained vowel phonation.',
      sparkline: [1.3, 1.2, 1.4, 1.2, 1.2]
    },
    {
      channel: 'face',
      name: 'Spontaneous Blink Interval',
      current: '16 blinks/min',
      baseline: '14 – 20 blinks/min',
      status: 'stable',
      trend: 'Optimal',
      description: 'Visual extraction of eye-aspect ratios from 30-second camera recordings.',
      sparkline: [17, 16, 18, 15, 16]
    },
    {
      channel: 'motor',
      name: 'Pronation-Supination Rhythm',
      current: '2.4 Hz',
      baseline: '2.3 – 2.8 Hz',
      status: 'improving',
      trend: '+0.2 Hz vs last week',
      description: 'Rapid alternating forearm rotation cadence measured via consumer camera stream.',
      sparkline: [2.1, 2.2, 2.3, 2.4, 2.4]
    },
    {
      channel: 'symptoms',
      name: 'Reported Daily Fatigue',
      current: '1 / 10',
      baseline: '1 – 3 / 10',
      status: 'stable',
      trend: 'Low severity',
      description: 'Self-reported visual analogue scoring recorded during morning check-in.',
      sparkline: [2, 1, 2, 1, 1]
    },
  ];

  const filterTabs: { id: ChannelType; label: string }[] = [
    { id: 'all', label: 'All Channels' },
    { id: 'voice', label: 'Voice & Speech' },
    { id: 'face', label: 'Facial Dynamics' },
    { id: 'motor', label: 'Movement & Motor' },
    { id: 'symptoms', label: 'Symptom Trajectory' },
  ];

  const filtered = selectedChannel === 'all'
    ? biomarkerMetrics
    : biomarkerMetrics.filter((m) => m.channel === selectedChannel);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Digital Biomarker Channels
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Objective computational features derived from continuous, non-clinical sensor observations.
        </p>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-4">
        {filterTabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setSelectedChannel(tab.id)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              selectedChannel === tab.id
                ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {filtered.map((metric, i) => (
          <div
            key={i}
            className="rounded-2xl bg-[#111827] border border-slate-800 p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 hover:border-slate-700 transition-all"
          >
            <div className="max-w-xl">
              <div className="flex items-center gap-3">
                <h3 className="text-base font-semibold text-white">{metric.name}</h3>
                <StatusBadge status={metric.status} size="sm" />
              </div>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                {metric.description}
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 items-center gap-6 border-t md:border-t-0 pt-4 md:pt-0 border-slate-800">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-500">Current</span>
                <p className="text-base font-bold text-white">{metric.current}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-500">Personal Baseline</span>
                <p className="text-xs font-medium text-slate-300 font-mono">{metric.baseline}</p>
              </div>
              <div className="col-span-2 sm:col-span-1">
                <span className="text-[10px] uppercase font-mono text-slate-500">Recent Signal</span>
                <Sparkline data={metric.sparkline} width={100} height={24} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};