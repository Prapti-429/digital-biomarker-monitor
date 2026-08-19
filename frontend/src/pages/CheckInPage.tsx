import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { aiService, AIAnalysisResponse } from '../services/aiService';

const MOOD_VALUES: Record<string, number> = { better: 0.1, same: 0, different: 0.5, significant: 1 };
const SYMPTOMS = ['Vocal strain', 'Motor stiffness', 'Tremor sensations', 'Facial tightness', 'Brain fog', 'Sleep disruption'];
const PROMPTS = {
  English: [
    'Please describe how your day has been going in one or two natural sentences.',
    'Tell us something you did today and how it made you feel.',
    'Please read this sentence naturally, at your comfortable speaking pace.',
    'Describe your plans for tomorrow using your normal voice.',
    'In your own words, tell us what has felt different today, if anything.',
  ],
  Hindi: [
    'कृपया अपने दिन के बारे में एक या दो सामान्य वाक्यों में बताइए।',
    'आज आपने ऐसा क्या किया जो आपको अच्छा लगा? अपने सामान्य तरीके से बताइए।',
    'कृपया इस वाक्य को अपनी सामान्य गति और आवाज़ में पढ़िए।',
    'कल के लिए आपकी क्या योजना है? अपने शब्दों में बताइए।',
    'अगर आज कुछ अलग महसूस हुआ हो, तो अपने सामान्य तरीके से उसके बारे में बताइए।',
  ],
} as const;

function clamp(v: number, lo: number, hi: number) { return Math.min(hi, Math.max(lo, v)); }
function average(values: number[]) { return values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0; }
function variability(values: number[]) { const m = average(values); return Math.sqrt(average(values.map(v => (v - m) ** 2))); }

async function analyzeAudio(blob: Blob) {
  const Ctx = window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!Ctx) throw new Error('Web Audio is not supported.');
  const ctx = new Ctx();
  try {
    const buffer = await ctx.decodeAudioData(await blob.arrayBuffer());
    const channel = buffer.getChannelData(0);
    const count = Math.min(channel.length, 200000);
    const samples = Array.from({ length: count }, (_, i) => channel[Math.floor(i * channel.length / count)]);
    const rms = Math.sqrt(average(samples.map(x => x * x)));
    let crossings = 0;
    for (let i = 1; i < samples.length; i++) if ((samples[i - 1] < 0) !== (samples[i] < 0)) crossings++;
    const zcr = crossings / Math.max(samples.length - 1, 1);
    const frameSize = Math.max(256, Math.floor(buffer.sampleRate * 0.025));
    const hop = Math.max(128, Math.floor(buffer.sampleRate * 0.01));
    let frames = 0, active = 0, pitchSum = 0, pitchCount = 0;
    for (let start = 0; start + frameSize < channel.length; start += hop) {
      let e = 0; for (let j = 0; j < frameSize; j++) e += channel[start + j] ** 2;
      const fr = Math.sqrt(e / frameSize); frames++;
      if (fr > Math.max(rms * 0.35, 0.01)) {
        active++;
        let bestLag = 0, best = -Infinity;
        const minLag = Math.floor(buffer.sampleRate / 400), maxLag = Math.min(Math.floor(buffer.sampleRate / 70), frameSize - 1);
        for (let lag = minLag; lag <= maxLag; lag += 1) { let c = 0; for (let j = 0; j < frameSize - lag; j += 4) c += channel[start + j] * channel[start + j + lag]; if (c > best) { best = c; bestLag = lag; } }
        if (bestLag) { const p = buffer.sampleRate / bestLag; if (p >= 70 && p <= 400) { pitchSum += p; pitchCount++; } }
      }
    }
    return { rms, zcr: clamp(zcr, 0, 1), pitch: pitchCount ? pitchSum / pitchCount : 180, speechActivity: frames ? active / frames : 0 };
  } finally { await ctx.close(); }
}

type MotionMetrics = { faceMotion: number; luminanceVariability: number; blinkProxy: number; blinkRate: number; eyeOpening: number; gaitMotion: number; gaitVariability: number; gaitSymmetry: number; breathingRate: number; breathingVariability: number; headMotion: number; headVariability: number };

async function captureCameraMetrics(video: HTMLVideoElement, canvas: HTMLCanvasElement, seconds = 12): Promise<MotionMetrics> {
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  if (!ctx) throw new Error('Canvas is unavailable.');
  canvas.width = 192; canvas.height = 144;
  const frames: { motion: number; lum: number; eye: number; chest: number; head: number }[] = [];
  let previous: Uint8ClampedArray | null = null;
  const started = performance.now();
  while (performance.now() - started < seconds * 1000) {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const px = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    let totalLum = 0, motion = 0, eye = 0, chest = 0, head = 0, n = 0, eyeN = 0, chestN = 0, headN = 0;
    for (let y = 0; y < canvas.height; y += 2) for (let x = 0; x < canvas.width; x += 2) {
      const i = (y * canvas.width + x) * 4; const l = (0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2]) / 255; totalLum += l; n++;
      if (previous) motion += Math.abs(l - ((0.2126 * previous[i] + 0.7152 * previous[i + 1] + 0.0722 * previous[i + 2]) / 255));
      if (y > 35 && y < 65 && x > 45 && x < 147) { eye += l; eyeN++; }
      if (y > 75 && y < 125 && x > 55 && x < 137) { chest += l; chestN++; }
      if (y > 15 && y < 75 && x > 55 && x < 137) { head += l; headN++; }
    }
    frames.push({ motion: motion / Math.max(n, 1), lum: totalLum / Math.max(n, 1), eye: eye / Math.max(eyeN, 1), chest: chest / Math.max(chestN, 1), head: head / Math.max(headN, 1) });
    previous = new Uint8ClampedArray(px);
    await new Promise(r => window.setTimeout(r, 200));
  }
  const motions = frames.map(f => f.motion), lums = frames.map(f => f.lum), eyes = frames.map(f => f.eye), chests = frames.map(f => f.chest), heads = frames.map(f => f.head);
  const eyeChanges = eyes.slice(1).map((v, i) => Math.abs(v - eyes[i]));
  const blinkEvents = eyeChanges.filter(v => v > Math.max(0.015, variability(eyes) * 1.5)).length;
  const chestChanges = chests.slice(1).map((v, i) => Math.abs(v - chests[i]));
  const peaks = chestChanges.filter((v, i) => i > 0 && i < chestChanges.length - 1 && v > chestChanges[i - 1] && v >= chestChanges[i + 1] && v > variability(chestChanges)).length;
  const minutes = seconds / 60;
  const breathingRate = clamp(peaks / Math.max(minutes, 0.1), 0, 60);
  const leftMotion = average(frames.map((f, i) => f.motion * (i % 2 ? 1 : 0.9)));
  const rightMotion = average(frames.map((f, i) => f.motion * (i % 2 ? 0.9 : 1)));
  return {
    faceMotion: average(motions), luminanceVariability: variability(lums), blinkProxy: clamp(blinkEvents / Math.max(frames.length, 1), 0, 1), blinkRate: clamp(blinkEvents / Math.max(minutes, 0.1), 0, 120), eyeOpening: clamp(1 - variability(eyes) * 4, 0, 1),
    gaitMotion: average(motions), gaitVariability: variability(motions), gaitSymmetry: clamp(1 - Math.abs(leftMotion - rightMotion) / Math.max(leftMotion + rightMotion, 0.0001), 0, 1), breathingRate, breathingVariability: variability(chestChanges), headMotion: average(heads.slice(1).map((v, i) => Math.abs(v - heads[i]))), headVariability: variability(heads),
  };
}

function Info({ text }: { text: string }) { return <span title={text} aria-label={text} className="inline-flex ml-1 w-4 h-4 items-center justify-center rounded-full border border-slate-600 text-[10px] text-slate-400 cursor-help">i</span>; }

export const CheckInPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1), [mood, setMood] = useState('same'), [fatigue, setFatigue] = useState(2), [symptoms, setSymptoms] = useState<string[]>([]);
  const [language, setLanguage] = useState<'English' | 'Hindi'>('English');
  const [prompt, setPrompt] = useState(PROMPTS.English[0]);
  const [voiceRecording, setVoiceRecording] = useState(false), [voiceRecorded, setVoiceRecorded] = useState(false), [voiceSeconds, setVoiceSeconds] = useState(0);
  const [voiceFeatures, setVoiceFeatures] = useState<Awaited<ReturnType<typeof analyzeAudio>> | null>(null);
  const [metrics, setMetrics] = useState<MotionMetrics | null>(null), [capturing, setCapturing] = useState(false), [cameraError, setCameraError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AIAnalysisResponse | null>(null), [analyzing, setAnalyzing] = useState(false), [error, setError] = useState<string | null>(null);
  const recorder = useRef<MediaRecorder | null>(null), chunks = useRef<Blob[]>([]), stream = useRef<MediaStream | null>(null), videoRef = useRef<HTMLVideoElement | null>(null), canvasRef = useRef<HTMLCanvasElement | null>(null);

  const chooseLanguage = (lang: 'English' | 'Hindi') => { setLanguage(lang); const list = PROMPTS[lang]; setPrompt(list[Math.floor(Math.random() * list.length)]); };
  const anotherPrompt = () => { const list = PROMPTS[language]; const alternatives = list.filter(p => p !== prompt); setPrompt(alternatives[Math.floor(Math.random() * alternatives.length)]); };

  const startVoice = async () => {
    setError(null); try {
      const s = await navigator.mediaDevices.getUserMedia({ audio: true }); stream.current = s;
      const mime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
      const r = new MediaRecorder(s, { mimeType: mime }); chunks.current = [];
      r.ondataavailable = e => { if (e.data.size) chunks.current.push(e.data); };
      r.onstop = async () => { try { setVoiceFeatures(await analyzeAudio(new Blob(chunks.current, { type: r.mimeType }))); setVoiceRecorded(true); } catch { setError('The recording was saved but acoustic extraction could not be completed.'); } finally { s.getTracks().forEach(t => t.stop()); } };
      r.start(250); recorder.current = r; setVoiceSeconds(0); setVoiceRecording(true);
    } catch { setError('Microphone permission was not available. You can continue with other modalities.'); }
  };
  const stopVoice = () => { if (recorder.current?.state !== 'inactive') recorder.current?.stop(); recorder.current = null; setVoiceRecording(false); };
  useEffect(() => { if (!voiceRecording) return; const id = window.setInterval(() => setVoiceSeconds(v => { if (v >= 10) { stopVoice(); return 10; } return v + 1; }), 1000); return () => clearInterval(id); }, [voiceRecording]);

  const startCamera = useCallback(async () => { try { const s = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' }, audio: false }); if (videoRef.current) videoRef.current.srcObject = s; stream.current = s; } catch { setCameraError('Camera permission was not available. You can continue without camera modalities.'); } }, []);
  const stopCamera = useCallback(() => { stream.current?.getTracks().forEach(t => t.stop()); stream.current = null; }, []);
  useEffect(() => { if (step === 3) startCamera(); else stopCamera(); return () => stopCamera(); }, [step, startCamera, stopCamera]);
  const capture = async () => { if (!videoRef.current || !canvasRef.current) return; setCapturing(true); setError(null); try { setMetrics(await captureCameraMetrics(videoRef.current, canvasRef.current)); } catch (e: any) { setError(e.message || 'Camera analysis failed.'); } finally { setCapturing(false); } };

  const analyze = async () => {
    setAnalyzing(true); setError(null);
    try {
      const payload = { fatigue, mood_deviation: MOOD_VALUES[mood] ?? 0, symptom_burden: symptoms.length / SYMPTOMS.length, ...(voiceFeatures ? { voice_rms: voiceFeatures.rms, voice_zero_crossing_rate: voiceFeatures.zcr, voice_pitch_hz: voiceFeatures.pitch, voice_speech_activity: voiceFeatures.speechActivity, voice_language: language } : {}), ...(metrics ? { face_motion: metrics.faceMotion, face_luminance_variability: metrics.luminanceVariability, face_blink_proxy: metrics.blinkProxy, blink_rate_per_minute: metrics.blinkRate, eye_opening_proxy: metrics.eyeOpening, gait_motion: metrics.gaitMotion, gait_variability: metrics.gaitVariability, gait_symmetry_proxy: metrics.gaitSymmetry, breathing_rate_per_minute: metrics.breathingRate, breathing_variability: metrics.breathingVariability, head_motion: metrics.headMotion, head_motion_variability: metrics.headVariability } : {}), source_duration_seconds: Math.max(voiceSeconds, metrics ? 12 : 0) };
      setAnalysis(await aiService.analyze(payload)); setStep(4);
    } catch (e: any) { if (e?.response?.status === 401 || e?.status === 401) navigate('/login'); else setError(e?.response?.data?.detail || e?.message || 'AI analysis could not be completed.'); } finally { setAnalyzing(false); }
  };

  const cards = useMemo(() => [
    ['Voice / speech', voiceFeatures ? 'Captured' : 'Missing', 'Pitch, loudness, zero-crossing and speech activity.'],
    ['Face dynamics', metrics ? 'Captured' : 'Missing', 'Frame-to-frame facial motion and light variability.'],
    ['Eyes / blink', metrics ? `${metrics.blinkRate.toFixed(1)}/min` : 'Missing', 'A camera-based eye/blink proxy; lighting affects accuracy.'],
    ['Gait / movement', metrics ? 'Captured' : 'Missing', 'Whole-frame movement proxy; not a clinical gait test.'],
    ['Breathing', metrics ? `${metrics.breathingRate.toFixed(1)}/min` : 'Missing', 'Visual chest-motion breathing-rate proxy.'],
    ['Head movement', metrics ? 'Captured' : 'Missing', 'Upper-frame motion proxy.'],
  ], [voiceFeatures, metrics]);

  return <div className="max-w-4xl mx-auto space-y-6 py-4">
    <div><div className="flex justify-between text-xs text-slate-400 mb-2"><span>STEP {step} OF 4</span><span className="text-sky-400">MULTIMODAL LONGITUDINAL CHECK-IN</span></div><div className="h-2 bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-gradient-to-r from-sky-400 to-teal-400" style={{ width: `${step * 25}%` }} /></div></div>
    {error && <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">{error}</div>}

    {step === 1 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6">
      <div><h2 className="text-xl font-bold text-white">Your baseline check-in <Info text="NUVYRA compares repeated observations with your own baseline rather than comparing you with other people." /></h2><p className="text-sm text-slate-400 mt-1">A few simple questions establish today's context.</p></div>
      <div className="grid sm:grid-cols-2 gap-3">{[['better','Better than usual'],['same','About the same'],['different','A little different'],['significant','Noticeably different']].map(([id,label]) => <button key={id} onClick={() => setMood(id)} className={`p-4 rounded-xl border text-left ${mood === id ? 'border-sky-500 bg-sky-500/10 text-sky-200' : 'border-slate-800 bg-slate-900 text-slate-300'}`}>{label}</button>)}</div>
      <label className="block text-sm text-slate-300">Fatigue <Info text="A self-rated 0–10 measure of how tired or low-energy you feel. It is not a medical test." /><span className="float-right text-sky-400">{fatigue}/10</span><input className="w-full mt-3" type="range" min="0" max="10" value={fatigue} onChange={e => setFatigue(Number(e.target.value))} /></label>
      <div><p className="text-sm text-slate-300 mb-2">Anything you noticed? <Info text="These are context signals. Selecting one does not mean you have a medical condition." /></p><div className="flex flex-wrap gap-2">{SYMPTOMS.map(s => <button key={s} onClick={() => setSymptoms(v => v.includes(s) ? v.filter(x => x !== s) : [...v, s])} className={`px-3 py-2 rounded-lg text-xs border ${symptoms.includes(s) ? 'border-teal-500 bg-teal-500/10 text-teal-200' : 'border-slate-800 text-slate-400'}`}>{s}</button>)}</div></div>
      <button onClick={() => setStep(2)} className="w-full rounded-xl bg-gradient-to-r from-sky-500 to-teal-500 py-3 font-semibold text-slate-950">Continue to voice</button>
    </section>}

    {step === 2 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6">
      <div><h2 className="text-xl font-bold text-white">Voice & speech sample <Info text="Voice features are acoustic measurements such as pitch, loudness and speech activity. They are used for longitudinal change detection, not diagnosis." /></h2><p className="text-sm text-slate-400 mt-1">Choose a language first. Each check-in uses a different prompt.</p></div>
      <div className="grid grid-cols-2 gap-3">{(['English','Hindi'] as const).map(l => <button key={l} onClick={() => chooseLanguage(l)} className={`p-3 rounded-xl border font-semibold ${language === l ? 'border-sky-500 bg-sky-500/10 text-sky-200' : 'border-slate-800 text-slate-400'}`}>{l}</button>)}</div>
      <div className="rounded-xl bg-slate-900 border border-slate-800 p-4"><div className="text-xs uppercase tracking-wide text-slate-500 mb-2">Please say</div><p className="text-white leading-relaxed">{prompt}</p><button onClick={anotherPrompt} className="mt-3 text-xs text-sky-400">Use a different prompt</button></div>
      <div className="text-center"><button onClick={voiceRecording ? stopVoice : startVoice} className={`rounded-full px-8 py-4 font-semibold ${voiceRecording ? 'bg-rose-500 text-white' : 'bg-sky-500 text-slate-950'}`}>{voiceRecording ? `Stop • ${voiceSeconds}s` : voiceRecorded ? 'Record again' : 'Start recording'}</button><p className="text-xs text-slate-500 mt-3">Maximum 10 seconds. Your browser asks for microphone permission.</p></div>
      {voiceFeatures && <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">{[['Pitch',`${voiceFeatures.pitch.toFixed(0)} Hz`,'Average fundamental-frequency estimate.'],['Loudness',voiceFeatures.rms.toFixed(3),'Signal strength of the recording.'],['Speech activity',`${(voiceFeatures.speechActivity*100).toFixed(0)}%`,'Approximate portion containing speech-like energy.'],['Language',language,'The language selected for this prompt.']].map(([n,v,t]) => <div key={n} className="bg-slate-900 rounded-xl p-3"><div className="text-xs text-slate-500">{n}<Info text={t} /></div><div className="text-white font-semibold mt-1">{v}</div></div>)}</div>}
      <div className="flex gap-3"><button onClick={() => setStep(1)} className="flex-1 border border-slate-700 rounded-xl py-3 text-slate-300">Back</button><button onClick={() => setStep(3)} className="flex-1 bg-gradient-to-r from-sky-500 to-teal-500 rounded-xl py-3 font-semibold text-slate-950">Continue to camera</button></div>
    </section>}

    {step === 3 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6">
      <div><h2 className="text-xl font-bold text-white">Movement, eyes, breathing & head <Info text="The camera module extracts non-identifying numerical motion proxies in the browser. Results can be affected by camera position, lighting and movement conditions." /></h2><p className="text-sm text-slate-400 mt-1">Sit or stand comfortably in front of the camera and keep the view reasonably stable.</p></div>
      <div className="aspect-video bg-black rounded-xl overflow-hidden relative"><video ref={videoRef} autoPlay muted playsInline className="w-full h-full object-cover" />{cameraError && <div className="absolute inset-0 flex items-center justify-center p-6 text-center text-sm text-amber-200">{cameraError}</div>}</div><canvas ref={canvasRef} className="hidden" />
      <button disabled={capturing} onClick={capture} className="w-full bg-gradient-to-r from-sky-500 to-teal-500 rounded-xl py-3 font-semibold text-slate-950 disabled:opacity-50">{capturing ? 'Capturing 12-second multimodal sample…' : metrics ? 'Capture again' : 'Start camera capture'}</button>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{cards.map(([name,value,desc]) => <div key={name} className="bg-slate-900 rounded-xl border border-slate-800 p-4"><div className="text-sm font-semibold text-white">{name}<Info text={desc} /></div><div className="text-sky-400 mt-1 font-mono text-sm">{value}</div><p className="text-[11px] text-slate-500 mt-2">{desc}</p></div>)}</div>
      <div className="rounded-xl border border-slate-800 p-4 text-xs text-slate-500">Missing camera signals are handled as <b>missing</b>, not as normal values. The AI fusion model only uses signals actually available in this session.</div>
      <div className="flex gap-3"><button onClick={() => setStep(2)} className="flex-1 border border-slate-700 rounded-xl py-3 text-slate-300">Back</button><button disabled={analyzing} onClick={analyze} className="flex-1 bg-gradient-to-r from-sky-500 to-teal-500 rounded-xl py-3 font-semibold text-slate-950 disabled:opacity-50">{analyzing ? 'Running AI…' : 'Run multimodal AI'}</button></div>
    </section>}

    {step === 4 && analysis && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6">
      <div><h2 className="text-xl font-bold text-white">Your longitudinal AI result <Info text="This score summarizes deviation from your personal baseline. It is not a diagnosis." /></h2><p className="text-sm text-slate-400">Model {analysis.model_version} • {analysis.baseline_observations} baseline observations</p></div>
      <div className="grid sm:grid-cols-3 gap-3"><div className="rounded-xl bg-slate-900 p-5"><div className="text-xs text-slate-500">Stability score<Info text="A higher score means the current measured pattern is closer to your own previous pattern." /></div><div className="text-4xl font-bold text-white mt-1">{analysis.overall_score.toFixed(0)}</div></div><div className="rounded-xl bg-slate-900 p-5"><div className="text-xs text-slate-500">Trend<Info text="Direction compared with your recent personal baseline." /></div><div className="text-xl font-bold text-sky-400 mt-3">{analysis.trend}</div></div><div className="rounded-xl bg-slate-900 p-5"><div className="text-xs text-slate-500">Data quality<Info text="How much usable signal information was available in this session." /></div><div className="text-xl font-bold text-teal-400 mt-3">{Math.round(analysis.data_quality_score*100)}%</div></div></div>
      <div className="rounded-xl border border-slate-800 p-4"><p className="text-sm text-slate-200">{analysis.explanation}</p><p className="text-xs text-slate-500 mt-2">Persistence: {analysis.persistence_signal} • Confidence: {Math.round(analysis.confidence*100)}%</p></div>
      <div className="grid sm:grid-cols-2 gap-4"><div><h3 className="text-sm font-semibold text-white mb-2">Signals used</h3><div className="flex flex-wrap gap-2">{analysis.modalities_present.map(m => <span key={m} className="px-2 py-1 rounded-lg bg-teal-500/10 text-teal-300 text-xs">{m}</span>)}</div></div><div><h3 className="text-sm font-semibold text-white mb-2">Missing signals</h3><div className="flex flex-wrap gap-2">{analysis.missing_modalities.map(m => <span key={m} className="px-2 py-1 rounded-lg bg-slate-800 text-slate-400 text-xs">{m}</span>)}</div></div></div>
      <div><h3 className="text-sm font-semibold text-white mb-2">What the AI noticed</h3><ul className="space-y-2">{analysis.top_drivers.map(x => <li key={x} className="text-sm text-slate-300">• {x}</li>)}</ul></div>
      <div><h3 className="text-sm font-semibold text-white mb-2">About NUVYRA <Info text="NUVYRA is a longitudinal digital-biomarker prototype designed to organize repeated observations and surface changes for review." /></h3><p className="text-sm text-slate-400">NUVYRA combines voice, facial/eye dynamics, movement/gait proxies, breathing-related motion, head movement and self-reported context. It builds an individual baseline, handles missing signals explicitly, and uses robust change detection with an Isolation Forest when enough history exists.</p></div>
      <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-xs text-slate-400">{analysis.limitations.join(' ')}</div>
      <button onClick={() => navigate('/dashboard')} className="w-full rounded-xl bg-gradient-to-r from-sky-500 to-teal-500 py-3 font-semibold text-slate-950">View longitudinal dashboard</button>
    </section>}
  </div>;
};
