import React from 'react';

export const TimelinePage: React.FC = () => {
  const events = [
    {
      date: 'Today, 8:30 AM',
      title: 'Daily Check-in Completed',
      desc: '30s phonation audio and motor kinematics captured. All values within personal baseline.',
      type: 'checkin',
    },
    {
      date: 'Yesterday, 8:45 AM',
      title: 'Daily Check-in Completed',
      desc: 'Subtle motor speed variation noted; acoustic features remained optimal.',
      type: 'checkin',
    },
    {
      date: 'Oct 18, 2026',
      title: 'Weekly Baseline Synthesis',
      desc: 'Rolling 7-day stability index updated to 84/100.',
      type: 'system',
    },
    {
      date: 'Oct 12, 2026',
      title: 'Cohort Protocol Onboarding',
      desc: 'Initial baseline calibration established across voice, facial, and motor channels.',
      type: 'milestone',
    },
  ];

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Longitudinal Timeline
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Chronological record of telemetry sessions, baseline calibrations, and observation logs.
        </p>
      </div>

      <div className="relative pl-6 border-l border-slate-800 space-y-8">
        {events.map((ev, i) => (
          <div key={i} className="relative group">
            <div className="absolute -left-[31px] top-1.5 w-3 h-3 rounded-full bg-[#0B0F17] border-2 border-sky-400 group-hover:scale-125 transition-transform" />
            <span className="text-xs font-mono text-slate-500">{ev.date}</span>
            <div className="mt-1 rounded-xl bg-[#111827] border border-slate-800 p-5 hover:border-slate-700 transition-all">
              <h3 className="text-sm font-semibold text-white">{ev.title}</h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">{ev.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};