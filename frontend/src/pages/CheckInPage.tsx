import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { aiService, AIAnalysisResponse } from '../services/aiService';

const MOOD_VALUES: Record<string, number> = {
  better: 0.1,
  same: 0,
  different: 0.5,
  significant: 1,
};

const SYMPTOMS = [
  'Vocal strain',
  'Motor stiffness',
  'Tremor sensations',
  'Facial tightness',
  'Brain fog',
  'Sleep disruption',
];

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

async function analyzeAudio(blob: Blob): Promise<{
  rms: number;
  zcr: number;
  pitch: number;
  speechActivity: number;
}> {
  const AudioContextCtor = window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!AudioContextCtor) throw new Error('Web Audio is not supported by this browser.');

  const context = new AudioContextCtor();
  try {
    const buffer = await context.decodeAudioData(await blob.arrayBuffer());
    const channel = buffer.getChannelData(0);
    const step = Math.max(1, Math.floor(channel.length / 200000));
    const samples: number[] = [];
    for (let i = 0; i < channel.length; i += step) samples.push(channel[i]);

    let sumSquares = 0;
    let crossings = 0;
    let active = 0;
    for (let i = 0; i < samples.length; i += 1) {
      const value = samples[i];
      sumSquares += value * value;
      if (i > 0 && ((samples[i - 1] < 0 && value >= 0) || (samples[i - 1] >= 0 && value < 0))) crossings += 1;
    }

    const rms = Math.sqrt(sumSquares / Math.max(samples.length, 1));
    const zcr = crossings / Math.max(samples.length - 1, 1);
    const frameSize = Math.max(256, Math.floor(buffer.sampleRate * 0.025));
    const hop = Math.max(128, Math.floor(buffer.sampleRate * 0.010));
    let frames = 0;
    let activeFrames = 0;
    let pitchSum = 0;
    let pitchCount = 0;

    for (let start = 0; start + frameSize < channel.length; start += hop) {
      let energy = 0;
      for (let j = 0; j < frameSize; j += 1) {
        const x = channel[start + j];
        energy += x * x;
      }
      const frameRms = Math.sqrt(energy / frameSize);
      frames += 1;
      if (frameRms > Math.max(rms * 0.35, 0.01)) {
        activeFrames += 1;
        const minLag = Math.floor(buffer.sampleRate / 400);
        const maxLag = Math.floor(buffer.sampleRate / 70);
        let bestLag = 0;
        let bestCorrelation = -Infinity;
        for (let lag = minLag; lag <= Math.min(maxLag, frameSize - 1); lag += 1) {
          let corr = 0;
          for (let j = 0; j < frameSize - lag; j += 4) corr += channel[start + j] * channel[start + j + lag];
          if (corr > bestCorrelation) {
            bestCorrelation = corr;
            bestLag = lag;
          }
        }
        if (bestLag > 0) {
          const candidate = buffer.sampleRate / bestLag;
          if (candidate >= 70 && candidate <= 400) {
            pitchSum += candidate;
            pitchCount += 1;
          }
        }
      }
    }

    return {
      rms: Number(rms.toFixed(6)),
      zcr: Number(clamp(zcr, 0, 1).toFixed(6)),
      pitch: Number((pitchCount ? pitchSum / pitchCount : 180).toFixed(2)),
      speechActivity: Number((frames ? activeFrames / frames : 0).toFixed(4)),
    };
  } finally {
    await context.close();
  }
}

export const CheckInPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [mood, setMood] = useState('same');
  const [fatigue, setFatigue] = useState(2);
  const [symptoms, setSymptoms] = useState<string[]>([]);

  const [voiceRecording, setVoiceRecording] = useState(false);
  const [voiceRecorded, setVoiceRecorded] = useState(false);
  const [voiceSeconds, setVoiceSeconds] = useState(0);
  const [voiceFeatures, setVoiceFeatures] = useState<Awaited<ReturnType<typeof analyzeAudio>> | null>(null);
  const voiceRecorderRef = useRef<MediaRecorder | null>(null);
  const voiceChunksRef = useRef<Blob[]>([]);
  const voiceStreamRef = useRef<MediaStream | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [faceCapturing, setFaceCapturing] = useState(false);
  const [faceCaptured, setFaceCaptured] = useState(false);
  const [faceSeconds, setFaceSeconds] = useState(0);
  const [faceMotion, setFaceMotion] = useState<number | null>(null);
  const [faceLuminanceVariability, setFaceLuminanceVariability] = useState<number | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);

  const [analysis, setAnalysis] = useState<AIAnalysisResponse | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const stopVoiceStream = useCallback(() => {
    voiceStreamRef.current?.getTracks().forEach((track) => track.stop());
    voiceStreamRef.current = null;
  }, []);

  const startVoiceRecording = async () => {
    setAnalysisError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      voiceStreamRef.current = stream;
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';
      const recorder = new MediaRecorder(stream, { mimeType });
      voiceChunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) voiceChunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        const blob = new Blob(voiceChunksRef.current, { type: recorder.mimeType });
        try {
          setVoiceFeatures(await analyzeAudio(blob));
          setVoiceRecorded(true);
        } catch (error) {
          console.error(error);
          setAnalysisError('The voice sample was recorded, but acoustic feature extraction failed. You can continue without voice features.');
          setVoiceRecorded(true);
        } finally {
          stopVoiceStream();
        }
      };
      recorder.start(250);
      voiceRecorderRef.current = recorder;
      setVoiceSeconds(0);
      setVoiceRecording(true);
    } catch (error) {
      console.error(error);
      setAnalysisError('Microphone permission was not available. You can continue with the other monitoring signals.');
    }
  };

  const stopVoiceRecording = () => {
    if (voiceRecorderRef.current && voiceRecorderRef.current.state !== 'inactive') voiceRecorderRef.current.stop();
    voiceRecorderRef.current = null;
    setVoiceRecording(false);
  };

  useEffect(() => {
    if (!voiceRecording) return;
    const timer = window.setInterval(() => {
      setVoiceSeconds((current) => {
        if (current >= 10) {
          stopVoiceRecording();
          return 10;
        }
        return current + 1;
      });
    }, 1000);
    return () => window.clearInterval(timer);
  }, [voiceRecording]);

  const stopCamera = useCallback(() => {
    cameraStream?.getTracks().forEach((track) => track.stop());
    setCameraStream(null);
    setFaceCapturing(false);
  }, [cameraStream]);

  const startCamera = useCallback(async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' }, audio: false });
      setCameraStream(stream);
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch (error) {
      console.error(error);
      setCameraError('Camera permission was not available. The AI analysis can still use the survey and voice signals.');
    }
  }, []);

  useEffect(() => {
    if (step === 3) startCamera();
    else stopCamera();
    return () => stopCamera();
  }, [step, startCamera, stopCamera]);

  const captureFaceFeatures = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d', { willReadFrequently: true });
    if (!context) return;
    canvas.width = 160;
    canvas.height = 120;
    const frames: number[] = [];
    const luminances: number[] = [];
    let previous: Uint8ClampedArray | null = null;
    const started = performance.now();
    setFaceCapturing(true);
    setFaceSeconds(0);

    while (performance.now() - started < 10000) {
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
      let luminanceSum = 0;
      let difference = 0;
      for (let i = 0; i < pixels.length; i += 4) {
        const luminance = 0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2];
        luminanceSum += luminance;
        if (previous) difference += Math.abs(luminance - (0.2126 * previous[i] + 0.7152 * previous[i + 1] + 0.0722 * previous[i + 2]));
      }
      frames.push(difference / (canvas.width * canvas.height * 255));
      luminances.push(luminanceSum / (canvas.width * canvas.height * 255));
      previous = new Uint8ClampedArray(pixels);
      setFaceSeconds(Math.min(10, Math.floor((performance.now() - started) / 1000)));
      await new Promise((resolve) => window.setTimeout(resolve, 200));
    }

    const meanMotion = frames.reduce((a, b) => a + b, 0) / Math.max(frames.length, 1);
    const meanLum = luminances.reduce((a, b) => a + b, 0) / Math.max(luminances.length, 1);
    const lumVariance = Math.sqrt(luminances.reduce((sum, value) => sum + (value - meanLum) ** 2, 0) / Math.max(luminances.length, 1));
    setFaceMotion(Number(meanMotion.toFixed(6)));
    setFaceLuminanceVariability(Number(lumVariance.toFixed(6)));
    setFaceCaptured(true);
    setFaceCapturing(false);
  };

  const finishAnalysis = async () => {
    setAnalyzing(true);
    setAnalysisError(null);
    try {
      const result = await aiService.analyze({
        fatigue,
        mood_deviation: MOOD_VALUES[mood] ?? 0,
        symptom_burden: symptoms.length / SYMPTOMS.length,
        ...(voiceFeatures
          ? {
              voice_rms: voiceFeatures.rms,
              voice_zero_crossing_rate: voiceFeatures.zcr,
              voice_pitch_hz: voiceFeatures.pitch,
              voice_speech_activity: voiceFeatures.speechActivity,
            }
          : {}),
        ...(faceMotion !== null ? { face_motion: faceMotion } : {}),
        ...(faceLuminanceVariability !== null ? { face_luminance_variability: faceLuminanceVariability } : {}),
        source_duration_seconds: Math.max(voiceSeconds, faceSeconds),
      });
      setAnalysis(result);
    } catch (error: any) {
      console.error(error);
      if (error?.status === 401) {
        navigate('/login');
        return;
      }
      setAnalysisError(error?.message || 'AI analysis could not be completed. Please try the check-in again.');
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => () => {
    stopVoiceStream();
    cameraStream?.getTracks().forEach((track) => track.stop());
  }, [cameraStream, stopVoiceStream]);

  const toggleSymptom = (symptom: string) => {
    setSymptoms((current) => current.includes(symptom) ? current.filter((item) => item !== symptom) : [...current, symptom]);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 py-4">
      <div>
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
          <span>STEP {step} OF 4</span>
          <span className="uppercase font-semibold text-sky-400">
            {step === 1 && '1. Subjective state & symptoms'}
            {step === 2 && '2. Acoustic phonation sample'}
            {step === 3 && '3. Facial dynamics'}
            {step === 4 && '4. AI synthesis & verification'}
          </span>
        </div>
        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div className="bg-gradient-to-r from-sky-400 to-teal-400 h-full transition-all duration-300" style={{ width: `${(step / 4) * 100}%` }} />
        </div>
      </div>

      {analysisError && <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">{analysisError}</div>}

      {step === 1 && (
        <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl">
          <div>
            <h2 className="text-xl font-bold text-white">How are you feeling today?</h2>
            <p className="text-xs text-slate-400 mt-1">The model compares today's observations with your own longitudinal baseline.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              ['better', 'Better than baseline'],
              ['same', 'About the same'],
              ['different', 'A little different'],
              ['significant', 'Noticeably different'],
            ].map(([id, label]) => (
              <button key={id} type="button" onClick={() => setMood(id)} className={`p-4 rounded-xl text-left border ${mood === id ? 'bg-sky-500/10 border-sky-500 text-sky-200' : 'bg-slate-900/60 border-slate-800 text-slate-300'}`}>
                <div className="font-semibold text-sm">{label}</div>
              </button>
            ))}
          </div>
          <div className="pt-4 border-t border-slate-800 space-y-2">
            <div className="flex justify-between text-xs text-slate-300"><span>Fatigue index</span><span className="font-mono text-sky-400 font-bold">{fatigue} / 10</span></div>
            <input type="range" min="0" max="10" value={fatigue} onChange={(e) => setFatigue(Number(e.target.value))} className="w-full accent-sky-400" />
          </div>
          <div className="pt-4 border-t border-slate-800 space-y-3">
            <label className="block text-xs font-medium text-slate-300">Observations today (optional)</label>
            <div className="flex flex-wrap gap-2">
              {SYMPTOMS.map((symptom) => <button key={symptom} type="button" onClick={() => toggleSymptom(symptom)} className={`px-3 py-1.5 rounded-lg text-xs border ${symptoms.includes(symptom) ? 'bg-teal-500/20 border-teal-400 text-teal-300' : 'bg-slate-900 border-slate-800 text-slate-400'}`}>{symptoms.includes(symptom) ? '✓ ' : '+ '}{symptom}</button>)}
            </div>
          </div>
          <div className="flex justify-end"><button type="button" onClick={() => setStep(2)} className="bg-gradient-to-r from-sky-500 to-teal-500 text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-sm">Continue to Voice →</button></div>
        </section>
      )}

      {step === 2 && (
        <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl">
          <div><h2 className="text-xl font-bold text-white">Vocal acoustic sample</h2><p className="text-xs text-slate-400 mt-1">Your browser extracts acoustic features locally; the raw recording is not uploaded by this check-in.</p></div>
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-sm leading-relaxed italic text-center">“The clear morning sunlight illuminated the quiet autumn woods, revealing subtle shifts in the landscape.”</div>
          <div className="flex flex-col items-center justify-center py-6 space-y-4">
            <button type="button" onClick={voiceRecording ? stopVoiceRecording : startVoiceRecording} className={`w-20 h-20 rounded-full flex items-center justify-center ${voiceRecording ? 'bg-rose-500 text-white animate-pulse' : voiceRecorded ? 'bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400' : 'bg-sky-500 text-slate-950'}`}>
              {voiceRecording ? <div className="w-5 h-5 bg-white rounded-sm" /> : voiceRecorded ? '✓' : '🎙'}
            </button>
            <span className="text-xs text-slate-400 font-mono">{voiceRecording ? `Recording: ${voiceSeconds}s / 10s` : voiceRecorded ? 'Acoustic features extracted' : 'Record a 10-second sample'}</span>
            {voiceFeatures && <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-[11px] text-slate-400"><div><b className="text-white block">{voiceFeatures.rms.toFixed(4)}</b>RMS</div><div><b className="text-white block">{voiceFeatures.zcr.toFixed(3)}</b>ZCR</div><div><b className="text-white block">{voiceFeatures.pitch.toFixed(0)} Hz</b>Pitch proxy</div><div><b className="text-white block">{(voiceFeatures.speechActivity * 100).toFixed(0)}%</b>Speech activity</div></div>}
          </div>
          <div className="flex justify-between pt-4 border-t border-slate-800"><button type="button" onClick={() => setStep(1)} className="text-xs text-slate-400">← Back</button><button type="button" onClick={() => setStep(3)} disabled={voiceRecording} className="bg-gradient-to-r from-sky-500 to-teal-500 disabled:opacity-40 text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-sm">Continue to Face →</button></div>
        </section>
      )}

      {step === 3 && (
        <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl">
          <div><h2 className="text-xl font-bold text-white">Facial dynamics & motion</h2><p className="text-xs text-slate-400 mt-1">The browser measures frame-to-frame motion and luminance variability. It does not identify you or diagnose a condition.</p></div>
          <div className="relative aspect-video max-w-md mx-auto rounded-2xl bg-black overflow-hidden border border-slate-700 flex items-center justify-center">
            {cameraStream ? <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover scale-x-[-1]" /> : <div className="text-center p-6 text-slate-400 text-sm">Camera unavailable. You can continue with the other signals.</div>}
            <canvas ref={canvasRef} className="hidden" />
          </div>
          {cameraError && <p className="text-xs text-amber-300 text-center">{cameraError}</p>}
          <div className="flex flex-col items-center gap-3"><button type="button" onClick={captureFaceFeatures} disabled={!cameraStream || faceCapturing || faceCaptured} className="bg-teal-500 disabled:opacity-40 text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-sm">{faceCapturing ? `Capturing ${faceSeconds}s / 10s` : faceCaptured ? '✓ Facial motion captured' : 'Capture 10-second sample'}</button>{faceCaptured && <div className="grid grid-cols-2 gap-6 text-center text-xs text-slate-400"><div><b className="text-white block">{faceMotion?.toFixed(5)}</b>Frame motion</div><div><b className="text-white block">{faceLuminanceVariability?.toFixed(5)}</b>Luminance variability</div></div>}</div>
          <div className="flex justify-between pt-4 border-t border-slate-800"><button type="button" onClick={() => setStep(2)} className="text-xs text-slate-400">← Back</button><button type="button" onClick={() => setStep(4)} disabled={faceCapturing} className="bg-gradient-to-r from-sky-500 to-teal-500 disabled:opacity-40 text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-sm">Review & Analyze →</button></div>
        </section>
      )}

      {step === 4 && (
        <section className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl">
          {!analysis ? <>
            <div><span className="text-xs font-mono text-sky-400">PERSONALIZED AI INFERENCE</span><h2 className="text-2xl font-bold text-white mt-1">Synthesize today's signals</h2><p className="text-sm text-slate-400 mt-2">The model compares today's survey, acoustic and facial-motion features with your longitudinal baseline.</p></div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs"><div className="rounded-xl bg-slate-900 border border-slate-800 p-4"><span className="text-slate-500">Fatigue</span><b className="block text-white mt-1">{fatigue}/10</b></div><div className="rounded-xl bg-slate-900 border border-slate-800 p-4"><span className="text-slate-500">Symptoms</span><b className="block text-white mt-1">{symptoms.length}</b></div><div className="rounded-xl bg-slate-900 border border-slate-800 p-4"><span className="text-slate-500">Modalities</span><b className="block text-white mt-1">{2 + (voiceFeatures ? 1 : 0) + (faceMotion !== null ? 1 : 0)}</b></div></div>
            <button type="button" onClick={finishAnalysis} disabled={analyzing} className="w-full bg-gradient-to-r from-sky-500 to-teal-500 disabled:opacity-50 text-slate-950 font-bold py-3 rounded-xl">{analyzing ? 'Running personalized AI analysis…' : 'Run AI analysis'}</button>
          </> : <>
            <div className="flex items-start justify-between gap-4"><div><span className="text-xs font-mono text-teal-400">AI ANALYSIS COMPLETE</span><h2 className="text-2xl font-bold text-white mt-1">Your monitoring result</h2></div><span className="px-3 py-1 rounded-full bg-slate-800 text-xs text-slate-300">{analysis.trend}</span></div>
            <div className="rounded-2xl bg-gradient-to-br from-sky-950/50 to-teal-950/30 border border-sky-500/20 p-6 text-center"><div className="text-6xl font-black text-white">{analysis.overall_score.toFixed(0)}</div><div className="text-slate-400 text-sm">/ 100 observational stability score</div><div className="text-xs text-slate-500 mt-2">Confidence {(analysis.confidence * 100).toFixed(0)}% · {analysis.baseline_observations} baseline observations</div></div>
            <p className="text-sm text-slate-300 leading-relaxed">{analysis.explanation}</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">{analysis.features.map((feature) => <div key={feature.name} className="rounded-xl bg-slate-900 border border-slate-800 p-4"><div className="text-xs text-slate-500 uppercase">{feature.category}</div><div className="text-sm text-white mt-1">{feature.name.replace(/_/g, ' ')}</div>{feature.deviation !== null && feature.deviation !== undefined && <div className="text-xs text-slate-400 mt-1">Baseline deviation: {feature.deviation.toFixed(2)} SD-like units</div>}</div>)}</div>
            <div className="flex justify-end"><button type="button" onClick={() => navigate('/dashboard')} className="bg-gradient-to-r from-sky-500 to-teal-500 text-slate-950 font-semibold px-6 py-2.5 rounded-xl">Go to dashboard →</button></div>
          </>}
        </section>
      )}
    </div>
  );
};
