import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const CheckInPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<number>(1);
  const [mood, setMood] = useState<string>('same');
  const [fatigue, setFatigue] = useState<number>(2);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordedAudio, setRecordedAudio] = useState<boolean>(false);

  const handleFinish = () => {
    // Navigates back to dashboard upon completion
    navigate('/dashboard');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 py-4">
      {/* Header & Stepper */}
      <div>
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
          <span>STEP {step} OF 3</span>
          <span>{step === 1 ? 'SUBJECTIVE STATE' : step === 2 ? 'VOICE SAMPLE' : 'REVIEW'}</span>
        </div>
        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div 
            className="bg-sky-400 h-full transition-all duration-300 rounded-full"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>
      </div>

      {/* Step 1: Feeling & Symptoms */}
      {step === 1 && (
        <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6">
          <div>
            <h2 className="text-xl font-bold text-white">How are you feeling today?</h2>
            <p className="text-xs text-slate-400 mt-1">Select the option that best reflects your state compared to your usual baseline.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { id: 'better', label: 'Better than usual' },
              { id: 'same', label: 'About the same' },
              { id: 'different', label: 'A little different' },
              { id: 'significant', label: 'Noticeably different' },
            ].map((opt) => (
              <button
                key={opt.id}
                onClick={() => setMood(opt.id)}
                className={`p-4 rounded-xl text-left text-sm font-medium border transition-all ${
                  mood === opt.id
                    ? 'bg-sky-500/10 border-sky-500 text-sky-300'
                    : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          <div className="pt-4 border-t border-slate-800 space-y-2">
            <div className="flex justify-between text-xs text-slate-300 font-medium">
              <span>Fatigue / Exhaustion level</span>
              <span className="font-mono text-sky-400">{fatigue} / 10</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              value={fatigue}
              onChange={(e) => setFatigue(Number(e.target.value))}
              className="w-full accent-sky-400 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => setStep(2)}
              className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
            >
              Continue to Voice &rarr;
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Voice Sample Recording */}
      {step === 2 && (
        <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6">
          <div>
            <h2 className="text-xl font-bold text-white">Vocal Acoustic Sample</h2>
            <p className="text-xs text-slate-400 mt-1">Read the following phrase naturally in a clear, conversational voice.</p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-200 text-sm leading-relaxed italic text-center">
            "The clear morning sunlight illuminated the quiet autumn woods, revealing subtle shifts in the landscape."
          </div>

          <div className="flex flex-col items-center justify-center py-6 space-y-4">
            <button
              onClick={() => {
                if (isRecording) {
                  setIsRecording(false);
                  setRecordedAudio(true);
                } else {
                  setIsRecording(true);
                }
              }}
              className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                isRecording
                  ? 'bg-rose-500 text-white animate-pulse'
                  : recordedAudio
                  ? 'bg-emerald-500/20 border border-emerald-500 text-emerald-400'
                  : 'bg-sky-500 hover:bg-sky-400 text-slate-950'
              }`}
            >
              {isRecording ? (
                <div className="w-5 h-5 bg-white rounded-sm" />
              ) : (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 02-3-3V5a3 3 0 116 0v6a3 3 0 02-3 3z" />
                </svg>
              )}
            </button>
            <span className="text-xs text-slate-400 font-mono">
              {isRecording ? 'Recording active (10s)...' : recordedAudio ? 'Sample captured (10s)' : 'Click to start recording'}
            </span>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-slate-800">
            <button
              onClick={() => setStep(1)}
              className="text-xs text-slate-400 hover:text-white"
            >
              &larr; Back
            </button>
            <button
              onClick={() => setStep(3)}
              disabled={!recordedAudio && !isRecording}
              className="bg-sky-500 hover:bg-sky-400 disabled:opacity-40 disabled:pointer-events-none text-slate-950 font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
            >
              Continue to Review &rarr;
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Confirmation / Submit */}
      {step === 3 && (
        <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 sm:p-8 space-y-6 text-center">
          <div className="w-12 h-12 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-400 flex items-center justify-center mx-auto">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>

          <div>
            <h2 className="text-xl font-bold text-white">Daily Check-in Complete</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              Your telemetry observations have been recorded and merged with your longitudinal baseline profile.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-left text-xs space-y-2 font-mono text-slate-300">
            <div className="flex justify-between"><span>Subjective Mood:</span><span className="text-sky-400 capitalize">{mood}</span></div>
            <div className="flex justify-between"><span>Fatigue Index:</span><span className="text-sky-400">{fatigue}/10</span></div>
            <div className="flex justify-between"><span>Audio Telemetry:</span><span className="text-emerald-400">Captured (16kHz)</span></div>
          </div>

          <button
            onClick={handleFinish}
            className="w-full bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 text-slate-950 font-semibold py-3 rounded-xl text-sm transition-all"
          >
            Return to Dashboard
          </button>
        </div>
      )}
    </div>
  );
};