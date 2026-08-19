import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { NuvyraLogo } from '../common/NuvyraLogo';
import { useLanguage, AppLanguage } from '../../contexts/LanguageContext';
import { InfoButton } from '../common/InfoButton';

export const AppShell: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { language, setLanguage } = useLanguage();
  return <div className="min-h-screen bg-[#0B0F17] flex">
    <div className="hidden lg:block"><Sidebar /></div>
    {mobileOpen && <div className="fixed inset-0 z-50 flex lg:hidden"><div className="fixed inset-0 bg-black/70" onClick={() => setMobileOpen(false)} /><div className="relative z-10 w-64 bg-[#0E1524]"><Sidebar onCloseMobile={() => setMobileOpen(false)} /></div></div>}
    <div className="flex-1 flex flex-col min-w-0">
      <header className="min-h-16 border-b border-slate-800/80 px-4 sm:px-8 py-3 flex items-center justify-between bg-[#0B0F17]/90 backdrop-blur-md sticky top-0 z-30 gap-3">
        <div className="flex items-center space-x-3 lg:hidden"><button onClick={() => setMobileOpen(true)} className="p-2 rounded-lg bg-slate-800/80 text-slate-300" aria-label="Open menu"><svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" /></svg></button><NuvyraLogo size="sm" /></div>
        <div className="hidden lg:flex items-center space-x-2 text-xs text-slate-400"><span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" /><span>NUVYRA Platform — Personal baseline sync active</span></div>
        <div className="flex items-center gap-2 sm:gap-4"><div className="flex items-center gap-1 rounded-xl border border-slate-800 bg-slate-900 px-2 py-1.5"><label htmlFor="global-language" className="sr-only">Language</label><select id="global-language" value={language} onChange={e => setLanguage(e.target.value as AppLanguage)} className="bg-transparent text-xs text-slate-200 outline-none"><option value="English">English</option><option value="Hindi">हिन्दी</option><option value="French">Français</option></select><InfoButton title="Language">This language choice is saved on this device and is used by the multilingual check-in.</InfoButton></div><div className="text-right hidden sm:block"><span className="block text-xs font-medium text-slate-300">NUVYRA</span><span className="block text-[10px] text-slate-500 font-mono">Personal baseline</span></div><div className="w-8 h-8 rounded-full border border-sky-500/30 bg-sky-500/10 flex items-center justify-center text-sky-400 text-xs font-bold">NV</div></div>
      </header>
      <main className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto"><Outlet /></main>
      <footer className="border-t border-slate-800/60 py-6 px-4 sm:px-8 text-center text-xs text-slate-500 bg-[#0A0E16]"><p className="max-w-3xl mx-auto leading-relaxed"><strong className="text-slate-400 font-semibold">NUVYRA Research Platform:</strong> Longitudinal digital-biomarker monitoring prototype. It is not a medical device and does not diagnose, treat, or triage medical conditions.</p></footer>
    </div>
  </div>;
};
