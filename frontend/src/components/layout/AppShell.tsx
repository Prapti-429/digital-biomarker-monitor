import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { NuvyraLogo } from '../common/NuvyraLogo';

export const AppShell: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0B0F17] flex">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm" onClick={() => setMobileOpen(false)} />
          <div className="relative z-10 w-64 bg-[#0E1524]">
            <Sidebar onCloseMobile={() => setMobileOpen(false)} />
          </div>
        </div>
      )}

      {/* Main Container */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header / Mobile Bar */}
        <header className="h-16 border-b border-slate-800/80 px-4 sm:px-8 flex items-center justify-between bg-[#0B0F17]/80 backdrop-blur-md sticky top-0 z-30">
          <div className="flex items-center space-x-3 lg:hidden">
            <button
              onClick={() => setMobileOpen(true)}
              className="p-2 rounded-lg bg-slate-800/80 text-slate-300 hover:text-white"
              aria-label="Open menu"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <NuvyraLogo size="sm" />
          </div>

          <div className="hidden lg:flex items-center space-x-2 text-xs text-slate-400">
            <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
            <span>NUVYRA Platform — Continuous Baseline Sync Active</span>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right hidden sm:block">
              <span className="block text-xs font-medium text-slate-300">Cohort Beta-1</span>
              <span className="block text-[10px] text-slate-500 font-mono">ID: #NV-88219</span>
            </div>
            <div className="w-8 h-8 rounded-full border border-sky-500/30 bg-sky-500/10 flex items-center justify-center text-sky-400 text-xs font-bold">
              NV
            </div>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>

        {/* Responsible Non-Clinical Research Disclaimer */}
        <footer className="border-t border-slate-800/60 py-6 px-4 sm:px-8 text-center text-xs text-slate-500 bg-[#0A0E16]">
          <p className="max-w-3xl mx-auto leading-relaxed">
            <strong className="text-slate-400 font-semibold">NUVYRA Research Platform:</strong> Designed for longitudinal digital biomarker telemetry research and baseline signal monitoring. Not a medical device and not intended for clinical diagnosis, treatment prescription, or acute triage.
          </p>
        </footer>
      </div>
    </div>
  );
};