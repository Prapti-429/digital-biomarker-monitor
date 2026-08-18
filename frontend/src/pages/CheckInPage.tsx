import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

export const CheckInPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<number>(1);

  // Step 1: Subjective & Symptoms
  const [mood, setMood] = useState<string>('same');
  const [fatigue, setFatigue] = useState<number>(2);
  const [symptoms, setSymptoms] = useState<string[]>([]);

  // Step 2: Voice
  const [isVoiceRecording, setIsVoiceRecording] = useState<boolean>(false);
  const [voiceRecorded, setVoiceRecorded] = useState<boolean>(false);
  const [voiceSeconds, setVoiceSeconds] = useState<number>(0);

  // Step 3: Face / Camera
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [cameraActive, setCameraActive] = useState<boolean>(false);
  const [isFaceCapturing, setIsFaceCapturing] = useState<boolean>(false);
  const [faceCaptured, setFaceCaptured] = useState<boolean>(false);
  const [faceSeconds, setFaceSeconds] = useState<number>(0);
  const [cameraError, setCameraError] = useState<string | null>(null);

  // Voice recording timer simulation
  useEffect(() => {
    let interval: any;
    if (isVoiceRecording) {
      interval = setInterval(() => {
        setVoiceSeconds((prev) => {
          if (prev >= 10) {
            setIsVoiceRecording(false);
            setVoiceRecorded(true);
            return 10;
          }
          return prev + 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isVoiceRecording]);

  // Face recording timer simulation
  useEffect(() => {
    let interval: any;
    if (isFaceCapturing) {
      interval = setInterval(() => {
        setFaceSeconds((prev) => {
          if (prev >= 10) {
            setIsFaceCapturing(false);
            setFaceCaptured(true);
            return 10;
          }
          return prev + 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isFaceCapturing]);

  // Camera cleanup and initiation on Step 3
  const startCamera = async () => {
    setCameraError(null);
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
          audio: false,
        });
        setCameraStream(stream);
        setCameraActive(true);
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } else {
        setCameraError('Camera access not supported in this browser environment.');
      }
    } catch (err: any) {
      console.warn('Camera permission issue:', err);
      setCameraError('Camera permission denied or camera device unavailable. Simulator active.');
      setCameraActive(true);
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop());
      setCameraStream(null);
    }
    setCameraActive(false);
  };

  useEffect(() => {
    if (step === 3) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [step]);

  const toggleSymptom = (sym: string) => {
    setSymptoms((prev) =>
      prev.includes(sym) ? prev.filter((s) => s !== sym) : [...prev, sym]
    );
  };

  const handleFinish = () => {
    stopCamera();
    navigate('/dashboard');
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 py-4">
      {/* Progress Header */}
      <div>
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
          <span>STEP {step} OF 4</span>
          <span className="uppercase font-semibold text-sky-400">
            {step === 1 && '1. Subjective State & Symptoms'}
            {step === 2 && '2. Acoustic Phonation Sample'}
            {step === 3 && '3. Facial Dynamics & Micro-Symmetry'}
            {step === 4 && '4. Synthesis & Verification'}
          </span>
        </div>
        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div
            className="bg-gradient-to-r from-sky-400 to-teal-400 h-full transition-all duration-300 rounded-full"
            style={{ width: `${(step / 4) * 100}%` }}
          />
        </div>
      </div>

      {/* STEP 1: SUBJECTIVE & SYMPTOMS */}
      {step === 1 && (
        <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl">
          <div>
            <h2 className="text-xl font-bold text-white">How are you feeling today?</h2>
            <p className="text-xs text-slate-400 mt-1">
              Select your subjective state compared to your ongoing longitudinal baseline.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { id: 'better', label: 'Better than baseline', desc: 'Higher energy, clearer focus' },
              { id: 'same', label: 'About the same', desc: 'Steady state, consistent with baseline' },
              { id: 'different', label: 'A little different', desc: 'Mild shift in sensation or fatigue' },
              { id: 'significant', label: 'Noticeably different', desc: 'Pronounced variation observed' },
            ].map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setMood(opt.id)}
                className={`p-4 rounded-xl text-left border transition-all ${
                  mood === opt.id
                    ? 'bg-sky-500/10 border-sky-500 text-sky-200'
                    : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div className="font-semibold text-sm">{opt.label}</div>
                <div className="text-xs text-slate-400 mt-0.5">{opt.desc}</div>
              </button>
            ))}
          </div>

          {/* Fatigue Slider */}
          <div className="pt-4 border-t border-slate-800 space-y-2">
            <div className="flex justify-between text-xs text-slate-300 font-medium">
              <span>Fatigue & Muscle Exhaustion Index</span>
              <span className="font-mono text-sky-400 font-bold">{fatigue} / 10</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              value={fatigue}
              onChange={(e) => setFatigue(Number(e.target.value))}
              className="w-full accent-sky-400 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0 (None)</span>
              <span>5 (Moderate)</span>
              <span>10 (Severe)</span>
            </div>
          </div>

          {/* Quick Symptoms Multi-Select */}
          <div className="pt-4 border-t border-slate-800 space-y-3">
            <label className="block text-xs font-medium text-slate-300">
              Select any specific observations today (optional):
            </label>
            <div className="flex flex-wrap gap-2">
              {[
                'Vocal strain',
                'Motor stiffness',
                'Tremor sensations',
                'Facial tightness',
                'Brain fog',
                'Sleep disruption',
              ].map((sym) => (
                <button
                  key={sym}
                  type="button"
                  onClick={() => toggleSymptom(sym)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    symptoms.includes(sym)
                      ? 'bg-teal-500/20 border-teal-400 text-teal-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {symptoms.includes(sym) ? '✓ ' : '+ '}
                  {sym}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="button"
              onClick={() => setStep(2)}
              className="bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-sm transition-all shadow-md"
            >
              Continue to Voice &rarr;
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: VOICE SAMPLE */}
      {step === 2 && (
        <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl">
          <div>
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">Vocal Acoustic Sample</h2>
              <span className="text-xs font-mono bg-slate-800 px-2.5 py-1 rounded text-sky-400">
                16kHz Raw Extraction
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Read the standardized passage aloud at your natural rhythm and volume.
            </p>
          </div>

          {/* Reading Prompt */}
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-sm leading-relaxed italic text-center">
            "The clear morning sunlight illuminated the quiet autumn woods, revealing subtle shifts in the landscape."
          </div>

          {/* Waveform and Recorder */}
          <div className="flex flex-col items-center justify-center py-6 space-y-4">
            {/* Visualizer bars */}
            <div className="flex items-center gap-1.5 h-12">
              {[40, 65, 85, 30, 95, 70, 45, 80, 60, 90, 50, 75, 35, 60, 85].map((h, i) => (
                <div
                  key={i}
                  className={`w-1.5 rounded-full transition-all duration-150 ${
                    isVoiceRecording
                      ? 'bg-sky-400 animate-pulse'
                      : voiceRecorded
                      ? 'bg-emerald-400'
                      : 'bg-slate-700'
                  }`}
                  style={{
                    height: isVoiceRecording ? `${Math.max(15, (h * (Math.random() + 0.3)) % 48)}px` : '12px',
                  }}
                />
              ))}
            </div>

            <button
              type="button"
              onClick={() => {
                if (isVoiceRecording) {
                  setIsVoiceRecording(false);
                  setVoiceRecorded(true);
                } else {
                  setVoiceSeconds(0);
                  setIsVoiceRecording(true);
                }
              }}
              className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                isVoiceRecording
                  ? 'bg-rose-500 text-white animate-pulse shadow-lg shadow-rose-500/30'
                  : voiceRecorded
                  ? 'bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400'
                  : 'bg-sky-500 hover:bg-sky-400 text-slate-950 shadow-md shadow-sky-500/20'
              }`}
            >
              {isVoiceRecording ? (
                <div className="w-5 h-5 bg-white rounded-sm" />
              ) : voiceRecorded ? (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 02-3-3V5a3 3 0 116 0v6a3 3 0 02-3 3z" />
                </svg>
              )}
            </button>

            <span className="text-xs text-slate-400 font-mono">
              {isVoiceRecording
                ? `Recording speech: ${voiceSeconds}s / 10s`
                : voiceRecorded
                ? `Voice sample calibrated (${voiceSeconds}s)`
                : 'Click microphone to record 10-second sample'}
            </span>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="text-xs text-slate-400 hover:text-white"
            >
              &larr; Back to Symptoms
            </button>
            <button
              type="button"
              onClick={() => setStep(3)}
              disabled={!voiceRecorded && !isVoiceRecording}
              className="bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 disabled:opacity-40 disabled:pointer-events-none text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-sm transition-all"
            >
              Continue to Facial Dynamics &rarr;
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: FACIAL DYNAMICS & CAMERA */}
      {step === 3 && (
        <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6 shadow-xl">
          <div>
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">Facial Dynamics & Micro-Symmetry</h2>
              <span className="text-xs font-mono bg-teal-500/20 text-teal-300 border border-teal-500/30 px-2.5 py-1 rounded">
                Camera Telemetry
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Position your face in the target frame and hold a neutral, comfortable posture for 10 seconds.
            </p>
          </div>

          {/* Camera Viewport & Overlay */}
          <div className="relative aspect-video max-w-md mx-auto rounded-2xl bg-black overflow-hidden border border-slate-700 flex items-center justify-center">
            {cameraStream ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover scale-x-[-1]"
              />
            ) : (
              <div className="text-center p-6 space-y-3">
                <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <p className="text-xs text-slate-400 font-mono">
                  {cameraError || 'Initializing video sensor...'}
                </p>
              </div>
            )}

            {/* Target mesh overlay */}
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
              <div
                className={`w-44 h-56 rounded-[45%] border-2 transition-all duration-300 ${
                  isFaceCapturing
                    ? 'border-sky-400 animate-pulse shadow-[0_0_25px_rgba(14,165,233,0.35)]'
                    : faceCaptured
                    ? 'border-emerald-400'
                    : 'border-slate-500/60 border-dashed'
                }`}
              />
            </div>

            {/* In-viewport timer/badge */}
            {isFaceCapturing && (
              <div className="absolute top-3 right-3 bg-red-500/90 backdrop-blur-md px-2.5 py-1 rounded-full text-[11px] font-mono text-white flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-white animate-ping" />
                <span>Capturing {faceSeconds}s / 10s</span>
              </div>
            )}
          </div>

          {/* Capture Controls */}
          <div className="flex flex-col items-center justify-center space-y-3">
            <button
              type="button"
              onClick={() => {
                if (isFaceCapturing) {
                  setIsFaceCapturing(false);
                  setFaceCaptured(true);
                } else {
                  setFaceSeconds(0);
                  setIsFaceCapturing(true);
                }
              }}
              className={`px-6 py-2.5 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                isFaceCapturing
                  ? 'bg-rose-500 text-white'
                  : faceCaptured
                  ? 'bg-emerald-500/20 border border-emerald-500 text-emerald-400'
                  : 'bg-sky-500 hover:bg-sky-400 text-slate-950'
              }`}
            >
              {isFaceCapturing ? (
                <span>Stop Visual Sampling ({faceSeconds}s)</span>
              ) : faceCaptured ? (
                <span>✓ Facial Dynamics Captured</span>
              ) : (
                <span>Start 10s Facial Sampling</span>
              )}
            </button>
            <p className="text-[11px] text-slate-500">
              Evaluates spontaneous blink rate, eye aspect ratio, and bilateral micro-symmetry.
            </p>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={() => setStep(2)}
              className="text-xs text-slate-400 hover:text-white"
            >
              &larr; Back to Voice
            </button>
            <button
              type="button"
              onClick={() => setStep(4)}
              disabled={!faceCaptured && !isFaceCapturing}
              className="bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 disabled:opacity-40 disabled:pointer-events-none text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-sm transition-all"
            >
              Continue to Review &rarr;
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: REVIEW & SYNTHESIS */}
      {step === 4 && (
        <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6 text-center shadow-xl">
          <div className="w-14 h-14 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-400 flex items-center justify-center mx-auto">
            <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
            </svg>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white">Daily Check-in Complete</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto leading-relaxed">
              Your multimodal session has been processed and synthesized with your 30-day longitudinal baseline profile.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 text-left text-xs space-y-3 font-mono text-slate-300">
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-slate-500">Subjective Mood:</span>
              <span className="text-sky-400 font-semibold capitalize">{mood}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-slate-500">Fatigue Index:</span>
              <span className="text-sky-400 font-semibold">{fatigue} / 10</span>
            </div>
            <div className="flex justify-between border-b border-slate-800 pb-2">
              <span className="text-slate-500">Acoustic Speech Stream:</span>
              <span className="text-emerald-400 font-semibold">10s Captured (3.8 syll/s baseline)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Facial Kinematics:</span>
              <span className="text-emerald-400 font-semibold">16 blinks/min (Symmetry: 99.2%)</span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleFinish}
            className="w-full bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 text-slate-950 font-bold py-3.5 rounded-xl text-sm transition-all shadow-lg hover:shadow-sky-500/20"
          >
            Merge with Baseline & Return to Dashboard
          </button>
        </div>
      )}
    </div>
  );
};
