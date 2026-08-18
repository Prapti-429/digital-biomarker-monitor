import React from 'react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Privacy & System Preferences
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Manage how your multimodal digital biomarker data is secured and processed.
        </p>
      </div>

      {/* Privacy Guarantee Card */}
      <div className="rounded-2xl bg-gradient-to-br from-[#121B2B] to-[#0E1524] border border-sky-500/20 p-6 space-y-4">
        <h2 className="text-base font-bold text-white">Privacy-First Architecture</h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          NUVYRA is engineered specifically for privacy-conscious research. Acoustic and kinematic telemetry vectors are extracted and processed locally wherever possible. Raw media streams are never shared without explicit authorization.
        </p>
      </div>

      <div className="rounded-2xl bg-[#111827] border border-slate-800 p-6 space-y-6 divide-y divide-slate-800">
        <div className="flex items-center justify-between pt-2">
          <div>
            <h3 className="text-sm font-medium text-white">Anonymized Telemetry Identifier</h3>
            <p className="text-xs text-slate-500">Unique subject code used in data exports</p>
          </div>
          <span className="text-xs font-mono text-sky-400 bg-sky-500/10 px-3 py-1 rounded-lg border border-sky-500/20">
            NV-88219-BETA
          </span>
        </div>

        <div className="flex items-center justify-between pt-6">
          <div>
            <h3 className="text-sm font-medium text-white">Daily Check-in Reminder</h3>
            <p className="text-xs text-slate-500">Receive morning notification for 30s session</p>
          </div>
          <input type="checkbox" defaultChecked className="accent-sky-500 w-4 h-4 rounded cursor-pointer" />
        </div>

        <div className="flex items-center justify-between pt-6">
          <div>
            <h3 className="text-sm font-medium text-white">High-Frequency Audio Extraction</h3>
            <p className="text-xs text-slate-500">Capture 16kHz uncompressed acoustic features</p>
          </div>
          <input type="checkbox" defaultChecked className="accent-sky-500 w-4 h-4 rounded cursor-pointer" />
        </div>
      </div>
    </div>
  );
};