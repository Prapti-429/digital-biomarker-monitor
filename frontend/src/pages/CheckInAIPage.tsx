import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { aiService, AIAnalysisResponse } from '../services/aiService';

type Language = 'English' | 'Hindi' | 'French';
type VoiceFeatures = { rms: number; zcr: number; pitch: number; speechActivity: number };
const VOICE_DURATION_SECONDS = 20;
const FACE_DURATION_SECONDS = 10;
const prompts: Record<Language, string[]> = {
  English: ['Please describe how your day has been going in one or two natural sentences.', 'Tell us about one thing you did today and how it made you feel.', 'Describe something you noticed today using your normal voice.', 'Tell us about your plans for tomorrow in your usual speaking voice.', 'Describe something that made you smile today.', 'If anything felt different today, describe it in your own words.'],
  Hindi: ['कृपया अपने दिन के बारे में एक या दो सामान्य वाक्यों में बताइए।', 'आज आपने ऐसा क्या किया जो आपको अच्छा लगा? अपने सामान्य तरीके से बताइए।', 'आज आपने कुछ खास या अलग क्या देखा? अपनी सामान्य आवाज़ में बताइए।', 'कल की अपनी योजनाओं के बारे में सामान्य आवाज़ में बताइए।', 'आज ऐसी कौन-सी बात हुई जिससे आपको खुशी हुई?', 'अगर आज कुछ अलग महसूस हुआ हो, तो अपने शब्दों में बताइए।'],
  French: ['Décrivez votre journée en une ou deux phrases avec votre voix naturelle.', 'Parlez-nous d’une chose que vous avez faite aujourd’hui et de ce que vous avez ressenti.', 'Décrivez quelque chose que vous avez remarqué aujourd’hui naturellement.', 'Parlez-nous de vos projets pour demain avec votre voix habituelle.', 'Parlez-nous d’une chose qui vous a fait sourire aujourd’hui.', 'Si quelque chose vous a semblé différent aujourd’hui, décrivez-le avec vos propres mots.'],
};
const symptoms = ['Vocal strain', 'Motor stiffness', 'Tremor sensations', 'Facial tightness', 'Brain fog', 'Sleep disruption'];
const moodDeviation: Record<string, number> = { better: 0.1, same: 0, different: 0.5, significant: 1 };
function clamp(value: number, min: number, max: number) { return Math.min(max, Math.max(min, value)); }
function choosePrompt(language: Language, previous: string | null) { const choices = prompts[language].filter((item) => item !== previous); return choices[Math.floor(Math.random() * choices.length)] ?? prompts[language][0]; }

async function extractVoice(blob: Blob): Promise<VoiceFeatures> {
  const Context = window.AudioContext;
  if (!Context) throw new Error('Web Audio is not supported by this browser.');
  const context = new Context();
  try {
    const audio = await context.decodeAudioData(await blob.arrayBuffer());
    const data = audio.getChannelData(0);
    const step = Math.max(1, Math.floor(data.length / 160000));
    let sum = 0; let crossings = 0; let count = 0; let previous = 0;
    for (let i = 0; i < data.length; i += step) { const value = data[i]; sum += value * value; count += 1; if (i > 0 && ((previous < 0 && value >= 0) || (previous >= 0 && value < 0))) crossings += 1; previous = value; }
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
        const pitch = bestLag ? audio.sampleRate / bestLag : 0; if (pitch >= 70 && pitch <= 400) { pitchTotal += pitch; pitchN += 1; }
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
  const [language, setLanguage] = useState<Language>(() => { const saved = window.localStorage.getItem('nuvyra-language'); return saved === 'Hindi' || saved === 'French' ? saved : 'English'; });
  const [prompt, setPrompt] = useState(() => choosePrompt('English', null));
  const [voiceBusy, setVoiceBusy] = useState(false); const [voiceSeconds, setVoiceSeconds] = useState(0); const [voiceFeatures, setVoiceFeatures] = useState<VoiceFeatures | null>(null);
  const [faceBusy, setFaceBusy] = useState(false); const [faceSeconds, setFaceSeconds] = useState(0); const [faceMotion, setFaceMotion] = useState<number | null>(null); const [faceLum, setFaceLum] = useState<number | null>(null);
  const [mediaError, setMediaError] = useState<string | null>(null); const [result, setResult] = useState<AIAnalysisResponse | null>(null); const [loading, setLoading] = useState(false);
  const streamRef = useRef<MediaStream | null>(null); const recorderRef = useRef<MediaRecorder | null>(null); const videoRef = useRef<HTMLVideoElement | null>(null); const canvasRef = useRef<HTMLCanvasElement | null>(null); const previousPromptRef = useRef<string | null>(null);
  const languageLabel = useMemo(() => ({ English: 'English', Hindi: 'हिन्दी', French: 'Français' }[language]), [language]);
  useEffect(() => { window.localStorage.setItem('nuvyra-language', language); }, [language]);
  useEffect(() => () => { streamRef.current?.getTracks().forEach((track) => track.stop()); if (recorderRef.current?.state !== 'inactive') recorderRef.current?.stop(); }, []);
  const changeLanguage = (next: Language) => { setLanguage(next); const nextPrompt = choosePrompt(next, previousPromptRef.current); previousPromptRef.current = nextPrompt; setPrompt(nextPrompt); setVoiceFeatures(null); };
  const newPrompt = () => { const nextPrompt = choosePrompt(language, previousPromptRef.current ?? prompt); previousPromptRef.current = nextPrompt; setPrompt(nextPrompt); setVoiceFeatures(null); };

  const recordVoice = async () => {
    setMediaError(null); setVoiceFeatures(null); setVoiceSeconds(0);
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error('Microphone access is not supported.');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); streamRef.current = stream;
      const type = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm'; const recorder = new MediaRecorder(stream, { mimeType: type }); const chunks: Blob[] = [];
      recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = async () => { try { setVoiceFeatures(await extractVoice(new Blob(chunks, { type: recorder.mimeType }))); } catch { setMediaError('The 20-second recording was captured, but its acoustic features could not be calculated in this browser.'); } finally { stream.getTracks().forEach((track) => track.stop()); streamRef.current = null; setVoiceBusy(false); setVoiceSeconds(VOICE_DURATION_SECONDS); } };
      recorderRef.current = recorder; recorder.start(250); setVoiceBusy(true); const startedAt = performance.now();
      const tick = window.setInterval(() => { const elapsed = Math.min(VOICE_DURATION_SECONDS, Math.floor((performance.now() - startedAt) / 1000)); setVoiceSeconds(elapsed); if (elapsed >= VOICE_DURATION_SECONDS) window.clearInterval(tick); }, 100);
      window.setTimeout(() => { window.clearInterval(tick); if (recorder.state !== 'inactive') recorder.stop(); }, VOICE_DURATION_SECONDS * 1000);
    } catch { setVoiceBusy(false); setMediaError('Microphone permission was unavailable. You can continue without voice features.'); }
  };

  const captureFace = async () => {
    setMediaError(null); setFaceMotion(null); setFaceLum(null); setFaceSeconds(0);
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error('Camera access is not supported.');
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' }, audio: false }); streamRef.current = stream;
      if (!videoRef.current || !canvasRef.current) throw new Error('Camera preview is unavailable.'); videoRef.current.srcObject = stream; await videoRef.current.play();
      const canvas = canvasRef.current; canvas.width = 160; canvas.height = 120; const ctx = canvas.getContext('2d', { willReadFrequently: true }); if (!ctx) throw new Error('Camera processing is unavailable.');
      setFaceBusy(true); const motions: number[] = []; const luminances: number[] = []; let previous: Uint8ClampedArray | null = null; const startedAt = performance.now(); const end = startedAt + FACE_DURATION_SECONDS * 1000;
      while (performance.now() < end) { ctx.drawImage(videoRef.current, 0, 0, 160, 120); const pixels = ctx.getImageData(0, 0, 160, 120).data; let lum = 0; let diff = 0; for (let i = 0; i < pixels.length; i += 4) { const l = 0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2]; lum += l; if (previous) diff += Math.abs(l - (0.2126 * previous[i] + 0.7152 * previous[i + 1] + 0.0722 * previous[i + 2])); } motions.push(diff / (160 * 120 * 255)); luminances.push(lum / (160 * 120 * 255)); previous = new Uint8ClampedArray(pixels); setFaceSeconds(Math.min(FACE_DURATION_SECONDS, Math.floor((performance.now() - startedAt) / 1000))); await new Promise((resolve) => window.setTimeout(resolve, 200)); }
      const meanMotion = motions.reduce((a, b) => a + b, 0) / Math.max(motions.length, 1); const meanLum = luminances.reduce((a, b) => a + b, 0) / Math.max(luminances.length, 1); const variance = Math.sqrt(luminances.reduce((a, b) => a + (b - meanLum) ** 2, 0) / Math.max(luminances.length, 1)); setFaceMotion(Number(meanMotion.toFixed(6))); setFaceLum(Number(variance.toFixed(6))); setFaceSeconds(FACE_DURATION_SECONDS);
    } catch { setMediaError('Camera access was unavailable. You can continue without camera-derived features.'); } finally { streamRef.current?.getTracks().forEach((track) => track.stop()); streamRef.current = null; setFaceBusy(false); }
  };

  const analyze = async () => {
    setLoading(true); setMediaError(null);
    try {
      const data = await aiService.analyze({ fatigue, mood_deviation: moodDeviation[mood] ?? 0, symptom_burden: selectedSymptoms.length / symptoms.length,
        ...(voiceFeatures ? { voice_rms: voiceFeatures.rms, voice_zero_crossing_rate: voiceFeatures.zcr, voice_pitch_hz: voiceFeatures.pitch, voice_speech_activity: voiceFeatures.speechActivity, voice_language: language } : { voice_language: language }),
        ...(faceMotion !== null ? { face_motion: faceMotion } : {}), ...(faceLum !== null ? { face_luminance_variability: faceLum } : {}), source_duration_seconds: VOICE_DURATION_SECONDS });
      setResult(data);
    } catch (error: any) { if (error?.status === 401) navigate('/login'); else setMediaError(error?.message || 'AI analysis failed. Please try again.'); }
    finally { setLoading(false); }
  };
  const toggle = (value: string) => setSelectedSymptoms((current) => current.includes(value) ? current.filter((item) => item !== value) : [...current, value]);

  return <div className="max-w-3xl mx-auto space-y-6 py-4">
    <div className="flex items-center justify-between text-xs font-mono text-slate-400"><span>DAILY AI CHECK-IN · STEP {step}/4</span><span className="text-sky-400">PERSONAL BASELINE MODEL</span></div>
    {mediaError && <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-200">{mediaError}</div>}
    {step === 1 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6"><div><h2 className="text-xl font-bold text-white">Daily check-in</h2><p className="mt-2 text-sm text-slate-400">Choose the language you are most comfortable using. This controls your voice prompt.</p></div><div className="grid grid-cols-3 gap-2">{(['English', 'Hindi', 'French'] as Language[]).map((item) => <button key={item} type="button" onClick={() => changeLanguage(item)} className={`rounded-xl border px-3 py-3 text-sm font-semibold ${language === item ? 'border-sky-400 bg-sky-500/10 text-white' : 'border-slate-800 bg-slate-900 text-slate-400'}`}>{item === 'Hindi' ? 'हिन्दी' : item === 'French' ? 'Français' : item}</button>)}</div><div className="grid grid-cols-2 gap-3">{Object.entries({ better: 'Better than usual', same: 'About the same', different: 'A little different', significant: 'Noticeably different' }).map(([id, label]) => <button key={id} type="button" onClick={() => setMood(id)} className={`p-4 rounded-xl border text-left ${mood === id ? 'border-sky-500 bg-sky-500/10 text-white' : 'border-slate-800 bg-slate-900 text-slate-300'}`}>{label}</button>)}</div><div><div className="flex justify-between text-xs text-slate-300"><span>How tired do you feel?</span><span>{fatigue}/10</span></div><input aria-label="Fatigue" className="w-full mt-2" type="range" min="0" max="10" value={fatigue} onChange={(e) => setFatigue(Number(e.target.value))} /></div><div><p className="text-xs text-slate-400 mb-2">Anything you noticed today?</p><div className="flex flex-wrap gap-2">{symptoms.map((item) => <button key={item} type="button" onClick={() => toggle(item)} className={`px-3 py-1.5 rounded-lg border text-xs ${selectedSymptoms.includes(item) ? 'border-teal-400 bg-teal-500/10 text-teal-300' : 'border-slate-800 text-slate-400'}`}>{selectedSymptoms.includes(item) ? '✓ ' : '+ '}{item}</button>)}</div></div><button type="button" onClick={() => setStep(2)} className="w-full bg-gradient-to-r from-sky-500 to-teal-500 text-slate-950 font-semibold py-3 rounded-xl">Continue →</button></section>}
    {step === 2 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6"><div><h2 className="text-xl font-bold text-white">Voice check · {languageLabel}</h2><p className="mt-2 text-sm text-slate-400">The voice collection window is exactly 20 seconds. The browser extracts numerical acoustic features from the recording.</p></div><div className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-sm leading-6 text-slate-300"><strong className="text-white">Before you start:</strong> sit comfortably, use your normal speaking voice, speak at your usual pace and comfortable volume, and use a reasonably quiet place if possible. Natural pauses are okay. Do not deliberately change your voice.</div><div className="rounded-xl bg-slate-900 p-5 text-center text-slate-200"><p className="text-xs uppercase tracking-wide text-slate-500 mb-2">Today's prompt</p><p className="text-base leading-7 italic">“{prompt}”</p><button type="button" onClick={newPrompt} disabled={voiceBusy} className="mt-3 text-xs text-sky-300 underline disabled:opacity-50">Use a different prompt</button></div><div className="text-center"><div className="text-4xl font-mono font-bold text-white">{voiceBusy ? VOICE_DURATION_SECONDS - voiceSeconds : voiceFeatures ? '20' : VOICE_DURATION_SECONDS}</div><div className="text-xs text-slate-500 mt-1">seconds {voiceBusy ? 'remaining' : 'recording window'}</div></div><button type="button" disabled={voiceBusy} onClick={recordVoice} className="mx-auto block px-6 py-3 rounded-xl bg-sky-500 disabled:opacity-50 text-slate-950 font-semibold">{voiceBusy ? 'Recording…' : voiceFeatures ? '✓ 20-second voice sample captured' : 'Start 20-second recording'}</button>{voiceFeatures && <div className="grid grid-cols-4 gap-2 text-center text-xs text-slate-400"><div><b className="text-white block">{voiceFeatures.rms.toFixed(4)}</b>Sound level</div><div><b className="text-white block">{voiceFeatures.zcr.toFixed(3)}</b>Sound pattern</div><div><b className="text-white block">{voiceFeatures.pitch.toFixed(0)} Hz</b>Pitch estimate</div><div><b className="text-white block">{(voiceFeatures.speechActivity * 100).toFixed(0)}%</b>Speech activity</div></div>}<div className="flex justify-between"><button type="button" onClick={() => setStep(1)} className="text-slate-400">← Back</button><button type="button" onClick={() => setStep(3)} className="bg-teal-500 text-slate-950 px-5 py-2 rounded-xl">Continue →</button></div></section>}
    {step === 3 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6"><div><h2 className="text-xl font-bold text-white">Face and camera check</h2><p className="mt-2 text-sm text-slate-400">The camera sample lasts 10 seconds and is reduced to movement and lighting features in the browser.</p></div><div className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-sm leading-6 text-slate-300"><strong className="text-white">For the best camera result:</strong><ul className="mt-2 list-disc pl-5 space-y-1"><li>Sit comfortably and keep your face and upper head inside the frame.</li><li>Face the camera directly and keep it roughly at eye level.</li><li>Use even lighting so your face is clearly visible; avoid a very bright light directly behind you.</li><li>Keep your face visible and avoid covering it with your hand.</li><li>Stay naturally still. Do not deliberately exaggerate facial expressions or movements.</li><li>Blink normally and look naturally at the camera. Do not force your eyes open or force yourself to blink.</li><li>If a movement instruction appears, follow it naturally and at a comfortable pace.</li></ul><p className="mt-3 text-slate-400">NUVYRA uses visible changes in the camera image as computer estimates. Lighting, camera position and movement can affect these measurements. They are not medical tests.</p></div><video ref={videoRef} muted playsInline className="w-full max-w-md mx-auto rounded-xl bg-black aspect-video object-cover scale-x-[-1]" /><canvas ref={canvasRef} className="hidden" /><div className="text-center"><span className="text-3xl font-mono font-bold text-white">{faceBusy ? FACE_DURATION_SECONDS - faceSeconds : faceMotion !== null ? '10' : FACE_DURATION_SECONDS}</span><span className="ml-2 text-xs text-slate-500">seconds remaining</span></div><button type="button" disabled={faceBusy} onClick={captureFace} className="mx-auto block px-6 py-3 rounded-xl bg-teal-500 disabled:opacity-50 text-slate-950 font-semibold">{faceBusy ? 'Capturing camera sample…' : faceMotion !== null ? '✓ Camera sample captured' : 'Start camera check'}</button>{faceMotion !== null && <div className="grid grid-cols-2 gap-3 text-center text-xs text-slate-400"><div><b className="text-white block">{faceMotion.toFixed(5)}</b>Visible movement</div><div><b className="text-white block">{faceLum?.toFixed(5)}</b>Lighting variability</div></div>}<div className="flex justify-between"><button type="button" onClick={() => setStep(2)} className="text-slate-400">← Back</button><button type="button" onClick={() => setStep(4)} className="bg-sky-500 text-slate-950 px-5 py-2 rounded-xl">Review →</button></div></section>}
    {step === 4 && <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6">{!result ? <><h2 className="text-xl font-bold text-white">AI assessment</h2><p className="text-sm text-slate-400">NUVYRA compares today's available signals with your longitudinal personal baseline. Missing or low-quality signals are not treated as normal data.</p><div className="grid grid-cols-3 gap-3 text-center"><div className="bg-slate-900 rounded-xl p-4"><b className="text-white block">{fatigue}/10</b><span className="text-xs text-slate-500">Fatigue</span></div><div className="bg-slate-900 rounded-xl p-4"><b className="text-white block">{selectedSymptoms.length}</b><span className="text-xs text-slate-500">Observations</span></div><div className="bg-slate-900 rounded-xl p-4"><b className="text-white block">{[voiceFeatures, faceMotion !== null].filter(Boolean).length + 1}</b><span className="text-xs text-slate-500">Signal groups</span></div></div><button type="button" disabled={loading} onClick={analyze} className="w-full bg-gradient-to-r from-sky-500 to-teal-500 disabled:opacity-50 text-slate-950 font-semibold py-3 rounded-xl">{loading ? 'Running AI analysis…' : 'Analyze check-in'}</button></> : <><h2 className="text-xl font-bold text-white">AI result</h2><div className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">The result is an observational change signal, not a diagnosis. Interpret it alongside data quality, confidence and your personal history.</div><pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap break-words rounded-xl bg-slate-950 p-4 text-xs text-slate-300">{JSON.stringify(result, null, 2)}</pre><button type="button" onClick={() => navigate('/dashboard')} className="w-full bg-teal-500 text-slate-950 font-semibold py-3 rounded-xl">Return to dashboard</button></>}<button type="button" onClick={() => setStep(3)} className="text-slate-400">← Back</button></section>}
  </div>;
};

export default CheckInAIPage;
