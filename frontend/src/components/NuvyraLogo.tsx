import React from 'react';

export default function NuvyraLogo({ size = 32, showWordmark = true }: { size?: number; showWordmark?: boolean }) {
  return (
    <div className="flex items-center gap-2" aria-label="NUVYRA">
      <svg width={size} height={size} viewBox="0 0 40 40" fill="none" aria-hidden="true">
        <path d="M8 29V11l24 18V11" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M8 29c5-7 9-7 12 0s7 7 12 0" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"/>
      </svg>
      {showWordmark && <span className="font-semibold tracking-[0.18em]">NUVYRA</span>}
    </div>
  );
}
