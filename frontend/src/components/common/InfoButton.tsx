import React, { useState } from 'react';

interface InfoButtonProps {
  title: string;
  children: React.ReactNode;
}

export const InfoButton: React.FC<InfoButtonProps> = ({ title, children }) => {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative inline-flex">
      <button type="button" aria-label={`More information about ${title}`} aria-expanded={open} onClick={() => setOpen(v => !v)} className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-slate-600 text-[11px] font-bold text-slate-300 hover:border-sky-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-sky-500/40">i</button>
      {open && (
        <span role="tooltip" className="absolute right-0 top-7 z-40 w-72 rounded-xl border border-slate-700 bg-slate-950 p-3 text-left text-xs leading-5 text-slate-300 shadow-2xl">
          <span className="mb-1 block font-semibold text-white">{title}</span>
          {children}
        </span>
      )}
    </span>
  );
};
