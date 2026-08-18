import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { aiService, AIAnalysisResponse } from '../services/aiService';

const symptoms = ['Vocal strain', 'Motor stiffness', 'Tremor sensations', 'Facial tightness', 'Brain fog', 'Sleep disruption'];
const moodDeviation: Record<string, number> = { better: 0.1, same: 0, different: 0.5, significant: 1 };

function clamp(value: number, min: number, max: number) { return Math.min(max, Math.max(min, value)); }

async function extractVoice(blob: Blob) {
  const Context = window.AudioContext;
  if (!Context) throw new Error('Web Audio is not supported.');
  const context = new Context();
  try {
    const audio = await context.decodeAudioData(await blob.arrayBuffer());
    const data = audio.getChannelData(0);
    const step = Math.max(1, Math.floor(data.length / 160000));
    let sum = 0; let crossings = 0; let count = 0; let previous = 0;
    for (let i = 0; i < data.length; i += step) {
      const value = data[i]; sum += value * value; count += 1;
      if (i > 0 && ((previous < 0 && value >= 0) || (previous >= 0 && value < 0))) crossings += 1;
      previous = value;
    }
    const rms = Math.sqrt(sum / Math.max(count, 1));
    const zcr = crossings / Math.max(count - 1, 1);
    const frame = Math.max(256, Math.floor(audio.sampleRate * 0.025));
    const hop = Math.max(128, Math.floor(audio.sampleRate * 0.01));
    let frames = 0; let active = 0; let pitchTotal = 0; let pitchN = 0;
    for (let start = 0; start + frame < data.length; start += hop) {
      let energy = 0; for (let j = 0; j < frame; j += 1) energy += data[start + j] ** 2;
      const frameRms = Math.sqrt(energy / frame); frames += 1;
      if (frameRms > Math.max(rms * 0.35, 0.01)) {
        active += 1;
        const minLag = Math.floor(audio.sampleRate / 400); const maxLag = Math.min(Math.floor(audio.sampleRate / 70), frame - 1);
        let bestLag = 0; let best = -Infinity;
        for (let lag = minLag; lag <= maxLag; lag += 1) { let corr = 0; for (let j = 0; j < frame - lag; j += 4) corr += data[start + j] * data[start + j + lag]; if (corr > best) { best = corr; bestLag = lag; } }
        const pitch = bestLag ? audio.sampleRate / bestLag : 0;
        if (pitch >= 70 && pitch <= 400) { pitchTotal += pitch; pitchN += 1; }
      }
    }
    return { rms: Number(rms.toFixed(6)), zcr: Number(clamp(zcr, 0, 1).toFixed(6)), pitch: Number((pitchN ? pitchTotal / pitchN : 180).toFixed(2)), speechActivity: Number((frames ? active / frames : 0).toFixed(4)) };
  } finally { await context.close(); }
}

export const CheckInAIPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [mood, setMood] = useState('same');
  const [fatigue, setFatigue] = useState(2);
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [voiceBusy, setVoiceBusy] = useState(false);
  const [voiceFeatures, setVoiceFeatures] = useState<{ rms: number; zcr: number; pitch: number; speechActivity: number } | null>(null);
  const [faceBusy, setFaceBusy] = useState(false);
  const [faceMotion, setFaceMotion] = useState<number | null>(null);
  const [faceLum, setFaceLum] = useState<number | null>(null);
  const [mediaError, setMediaError] = useState<string | null>(null);
  const [result, setResult] = useState<AIAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const streamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    if (recorderRef.current?.state !== 'inactive') recorderRef.current?.stop();
  }, []);

  const recordVoice = async () => {
    setMediaError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const type = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
      const recorder = new MediaRecorder(stream, { mimeType: type });
      const chunks: Blob[] = [];
      recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = async () => {
        try { setVoiceFeatures(await extractVoice(new Blob(chunks, { type: recorder.mimeType }))); }
        catch { setMediaError('The recording succeeded but acoustic extraction was unavailable.'); }
        finally { stream.getTracks().forEach((track) => track.stop()); streamRef.current = null; setVoiceBusy(false); }
      };
      recorderRef.current = recorder; recorder.start(250); setVoiceBusy(true);
      window.setTimeout(() => { if (recorder.state !== 'inactive') recorder.stop(); }, 10000);
    } catch { setMediaError('Microphone permission was unavailable. You can continue without voice features.'); }
  };

  const captureFace = async () => {
    setMediaError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' }, audio: false });
      streamRef.current = stream;
      if (!videoRef.current || !canvasRef.current) return;
      videoRef.current.srcObject = stream; await videoRef.current.play();
      const canvas = canvasRef.current; canvas.width = 160; canvas.height = 120;
      const ctx = canvas.getContext('2d', { willReadFrequently: true }); if (!ctx) return;
      setFaceBusy(true);
      const motions: number[] = []; const luminances: number[] = []; let previous: Uint8ClampedArray | null = null;
      const end = performance.now() + 10000;
      while (performance.now() < end) {
        ctx.drawImage(videoRef.current, 0, 0, 160, 120); const pixels = ctx.getImageData(0, 0, 160, 120).data;
        let lum = 0; let diff = 0;
        for (let i = 0; i < pixels.length; i += 4) { const l = 0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2]; lum += l; if (previous) diff += Math.abs(l - (0.2126 * previous[i] + 0.7152 * previous[i + 1] + 0.0722 * previous[i + 2])); }
        motions.push(diff / (160 * 120 * 255)); luminances.push(lum / (160 * 120 * 255)); previous = new Uint8ClampedArray(pixels); await new Promise((resolve) => window.setTimeout(resolve, 200));
      }
      const meanMotion = motions.reduce((a, b) => a + b, 0) / Math.max(motions.length, 1); const meanLum = luminances.reduce((a, b) => a + b, 0) / Math.max(luminances.length, 1); const variance = Math.sqrt(luminances.reduce((a, b) => a + (b - meanLum) ** 2, 0) / Math.max(luminances.length, 1));
      setFaceMotion(Number(meanMotion.toFixed(6))); setFaceLum(Number(variance.toFixed(6)));
    } catch { setMediaError('Camera permission was unavailable. You can continue without facial-motion features.'); }
    finally { streamRef.current?.getTracks().forEach((track) => track.stop()); streamRef.current = null; setFaceBusy(false); }
  };

  const analyze = async () => {
    setLoading(true); setMediaError(null);
    try {
      const data = await aiService.analyze({
        fatigue, mood_deviation: moodDeviation[mood] ?? 0, symptom_burden: selectedSymptoms.length / symptoms.length,
        ...(voiceFeatures ? { voice_rms: voiceFeatures.rms, voice_zero_crossing_rate: voiceFeatures.zcr, voice_pitch_hz: voiceFeatures.pitch, voice_speech_activity: voiceFeatures.speechActivity } : {}),
        ...(faceMotion !== null ? { face_motion: faceMotion } : {}), ...(faceLum !== null ? { face_luminance_variability: faceLum } : {}),
        source_duration_seconds: 10,
      });
      setResult(data);
    } catch (error: any) { if (error?.status === 401) navigate('/login'); else setMediaError(error?.message || 'AI analysis failed.'); }
    finally { setLoading(false); }
  };

  const toggle = (value: string) => setSelectedSymptoms((current) => current.includes(value) ? current.filter((item) => item !== value) : [...current, value]);

  return <div className="max-w-3xl mx-auto space-y-6 py-4">
    <div className="flex items-center justify-between text-xs font-mono text-slate-400"><span>DAILY AI CHECK-IN · STEP {step}/4</span><span className="text-sky-400">PERSONAL BASELINE MODEL</span></div>
    {mediaError && <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-200">{mediaError}</div>}
    {step === 1 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6"><h2 className="text-xl font-bold text-white">Subjective state</h2><div className="grid grid-cols-2 gap-3">{Object.entries({ better: 'Better than baseline', same: 'About the same', different: 'A little different', significant: 'Noticeably different' }).map(([id, label]) => <button key={id} onClick={() => setMood(id)} className={`p-4 rounded-xl border text-left ${mood === id ? 'border-sky-500 bg-sky-500/10 text-white' : 'border-slate-800 bg-slate-900 text-slate-300'}`}>{label}</button>)}</div><div><div className="flex justify-between text-xs text-slate-300"><span>Fatigue</span><span>{fatigue}/10</span></div><input className="w-full mt-2" type="range" min="0" max="10" value={fatigue} onChange={(e) => setFatigue(Number(e.target.value))} /></div><div><p className="text-xs text-slate-400 mb-2">Observations</p><div className="flex flex-wrap gap-2">{symptoms.map((item) => <button key={item} onClick={() => toggle(item)} className={`px-3 py-1.5 rounded-lg border text-xs ${selectedSymptoms.includes(item) ? 'border-teal-400 bg-teal-500/10 text-teal-300' : 'border-slate-800 text-slate-400'}`}>{selectedSymptoms.includes(item) ? '✓ ' : '+ '}{item}</button>)}</div></div><button onClick={() => setStep(2)} className="w-full bg-gradient-to-r from-sky-500 to-teal-500 text-slate-950 font-semibold py-3 rounded-xl">Continue →</button></section>}
    {step === 2 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6"><h2 className="text-xl font-bold text-white">Acoustic sample</h2><p className="text-sm text-slate-400">Read the prompt naturally for 10 seconds. Raw audio is processed in the browser; only numerical features are sent to the backend.</p><div className="rounded-xl bg-slate-900 p-5 text-center italic text-slate-200">“The clear morning sunlight illuminated the quiet autumn woods, revealing subtle shifts in the landscape.”</div><button disabled={voiceBusy} onClick={recordVoice} className="mx-auto block px-6 py-3 rounded-xl bg-sky-500 disabled:opacity-50 text-slate-950 font-semibold">{voiceBusy ? 'Recording…' : voiceFeatures ? '✓ Voice features captured' : 'Record 10-second sample'}</button>{voiceFeatures && <div className="grid grid-cols-4 gap-2 text-center text-xs text-slate-400"><div><b className="text-white block">{voiceFeatures.rms.toFixed(4)}</b>RMS</div><div><b className="text-white block">{voiceFeatures.zcr.toFixed(3)}</b>ZCR</div><div><b className="text-white block">{voiceFeatures.pitch.toFixed(0)} Hz</b>Pitch</div><div><b className="text-white block">{(voiceFeatures.speechActivity * 100).toFixed(0)}%</b>Activity</div></div>}<div className="flex justify-between"><button onClick={() => setStep(1)} className="text-slate-400">← Back</button><button onClick={() => setStep(3)} className="bg-teal-500 text-slate-950 px-5 py-2 rounded-xl">Continue →</button></div></section>}
    {step === 3 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6"><h2 className="text-xl font-bold text-white">Facial motion sample</h2><p className="text-sm text-slate-400">A 10-second camera sample is reduced to motion/luminance features. No face identity is stored.</p><video ref={videoRef} muted playsInline className="w-full max-w-md mx-auto rounded-xl bg-black aspect-video object-cover scale-x-[-1]" /><canvas ref={canvasRef} className="hidden" /><button disabled={faceBusy} onClick={captureFace} className="mx-auto block px-6 py-3 rounded-xl bg-teal-500 disabled:opacity-50 text-slate-950 font-semibold">{faceBusy ? 'Capturing…' : faceMotion !== null ? '✓ Facial features captured' : 'Capture 10-second sample'}</button>{faceMotion !== null && <div className="grid grid-cols-2 gap-3 text-center text-xs text-slate-400"><div><b className="text-white block">{faceMotion.toFixed(5)}</b>Frame motion</div><div><b className="text-white block">{faceLum?.toFixed(5)}</b>Luminance variability</div></div>}<div className="flex justify-between"><button onClick={() => setStep(2)} className="text-slate-400">← Back</button><button onClick={() => setStep(4)} className="bg-sky-500 text-slate-950 px-5 py-2 rounded-xl">Review →</button></div></section>}
    {step === 4 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6">{!result ? <><h2 className="text-xl font-bold text-white">AI synthesis</h2><p className="text-sm text-slate-400">The backend learns your longitudinal baseline and produces an observational stability signal.</p><div className="grid grid-cols-3 gap-3 text-center"><div className="bg-slate-900 rounded-xl p-4"><b className="text-white block">{fatigue}/10</b><span className="text-xs text-slate-500">Fatigue</span></div><div className="bg-slate-900 rounded-xl p-4"><b className="text-white block">{selectedSymptoms.length}</b><span className="text-xs text-slate-500">Symptoms</span></div><div className="bg-slate-900 rounded-xl p-4"><b className="text-white block">{[voiceFeatures, faceMotion !== null].filter(Boolean).length + 1}</b><span className="text-xs text-slate-500">Signal groups</span></div></div><button disabled={loading} onClick={analyze} className="w-full bg-gradient-to-r from-sky-500 to-teal-500 disabled:opacity-50 text-slate-950 font-bold py-3 rounded-xl">{loading ? 'Running AI model…' : 'Run personalized AI analysis'}</button></> : <><div className="flex justify-between"><div><span className="text-xs text-teal-400 font-mono">AI ANALYSIS COMPLETE</span><h2 className="text-2xl font-bold text-white mt-1">Monitoring result</h2></div><span className="bg-slate-800 rounded-full px-3 py-1 text-xs text-slate-300">{result.trend}</span></div><div className="rounded-2xl bg-slate-900 p-6 text-center"><div className="text-6xl font-black text-white">{Math.round(result.overall_score)}</div><div className="text-sm text-slate-400">/100 observational stability</div><div className="text-xs text-slate-500 mt-2">Confidence {Math.round(result.confidence * 100)}% · {result.baseline_observations} baseline observations</div></div><p className="text-sm text-slate-300 leading-relaxed">{result.explanation}</p><div className="grid sm:grid-cols-2 gap-3">{result.features.map((feature) => <div key={feature.name} className="rounded-xl border border-slate-800 bg-slate-900 p-4"><span className="text-[10px] uppercase text-slate-500">{feature.category}</span><div className="text-sm text-white mt-1">{feature.name.replace(/_/g, ' ')}</div></div>)}</div><button onClick={() => navigate('/dashboard')} className="w-full bg-gradient-to-r from-sky-500 to-teal-500 text-slate-950 font-bold py-3 rounded-xl">Return to dashboard →</button><p className="text-[11px] text-slate-500">This is an observational digital-biomarker signal, not a diagnosis or medical decision.</p></>}{step === 4 && !result && <button onClick={() => setStep(3)} className="text-slate-400">← Back</button>}</section>}
  </div>;
};
