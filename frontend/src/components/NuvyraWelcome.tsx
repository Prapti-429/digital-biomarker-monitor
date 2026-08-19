import React, { useState } from 'react';

const streams = [
  ['🎙️','Voice & speech','We look at characteristics of how you normally speak and watch for changes over time.'],
  ['🙂','Facial dynamics','We observe natural facial movement during the camera check.'],
  ['👁️','Eyes & blinking','The camera estimates blinking and eye-opening patterns. This is not an eye examination.'],
  ['🚶','Movement & gait','We look at visible movement patterns during the check-in.'],
  ['🌬️','Breathing pattern','We may estimate visible rhythmic changes related to breathing. This is not a breathing test.'],
  ['🧭','Head movement','We measure visible changes in head position and movement.'],
];

export default function NuvyraWelcome({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const next = () => step < 3 ? setStep(step + 1) : onComplete();
  return <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
    <div className="w-full max-w-5xl">
      {step === 0 && <section className="text-center py-16">
        <div className="text-7xl mb-8">✦</div><p className="uppercase tracking-[0.3em] text-sm text-slate-400 mb-4">Welcome to NUVYRA</p>
        <h1 className="text-5xl md:text-7xl font-semibold tracking-tight">Your body has patterns.<br/><span className="text-slate-400">NUVYRA helps you notice them.</span></h1>
        <p className="max-w-2xl mx-auto text-lg text-slate-300 mt-8">We use everyday signals such as voice, facial movement, eye activity and movement to learn your own patterns over time.</p>
        <button onClick={next} className="mt-10 rounded-2xl px-7 py-4 bg-white text-slate-950 font-medium hover:scale-[1.02] transition">Let's explore →</button>
      </section>}
      {step === 1 && <section className="py-10"><p className="text-slate-400 mb-3">HOW IT WORKS</p><h2 className="text-4xl font-semibold">The signals we look at</h2><p className="text-slate-400 mt-3">Tap any signal to understand it in simple words.</p><div className="grid md:grid-cols-3 gap-4 mt-8">{streams.map(([icon,name,desc],i)=><button key={name} onClick={()=>setSelected(i)} className="text-left rounded-3xl border border-white/10 bg-white/[.04] p-6 hover:bg-white/[.08] transition"><span className="text-3xl">{icon}</span><h3 className="text-lg font-medium mt-4">{name}</h3>{selected===i&&<p className="text-sm text-slate-300 mt-3 leading-6">{desc}</p>}<span className="block text-xs text-slate-500 mt-4">ⓘ Tap to learn more</span></button>)}</div><button onClick={next} className="mt-8 rounded-2xl px-7 py-4 bg-white text-slate-950 font-medium">Continue →</button></section>}
      {step === 2 && <section className="text-center py-14"><p className="text-slate-400 uppercase tracking-widest text-sm">The important part</p><h2 className="text-5xl font-semibold mt-4">We don't compare you<br/><span className="text-slate-400">to everyone else.</span></h2><div className="max-w-2xl mx-auto mt-10 rounded-3xl border border-white/10 bg-white/[.04] p-8"><div className="text-5xl">●</div><h3 className="text-2xl mt-5">Your personal baseline</h3><p className="text-slate-300 mt-3 leading-7">NUVYRA learns what is usual for you. As you continue checking in, it looks for meaningful changes from your own pattern.</p></div><button onClick={next} className="mt-8 rounded-2xl px-7 py-4 bg-white text-slate-950 font-medium">See how it works →</button></section>}
      {step === 3 && <section className="text-center py-14"><h2 className="text-5xl font-semibold">A few signals.<br/><span className="text-slate-400">One clearer picture.</span></h2><div className="flex flex-wrap justify-center items-center gap-3 my-12 text-slate-300"><span>Measure</span><span>→</span><span>Check quality</span><span>→</span><span>Learn your baseline</span><span>→</span><span>Understand change</span></div><p className="max-w-xl mx-auto text-slate-300">NUVYRA combines available signals with AI and explains the result in everyday language. It is a monitoring and research system, not a diagnosis.</p><button onClick={next} className="mt-10 rounded-2xl px-8 py-4 bg-white text-slate-950 font-semibold">Start using NUVYRA ✦</button></section>}
      <div className="flex justify-center gap-2 mt-4">{[0,1,2,3].map(i=><span key={i} className={`h-1.5 rounded-full transition-all ${i===step?'w-8 bg-white':'w-2 bg-white/20'}`}/>)}</div>
    </div>
  </div>;
}
