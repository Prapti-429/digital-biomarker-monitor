import React from 'react';

interface NuvyraLogoProps {
  className?: string;
  showWordmark?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const NuvyraLogo: React.FC<NuvyraLogoProps> = ({ 
  className = '', 
  showWordmark = true,
  size = 'md' 
}) => {
  const iconSizes = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10',
  };

  const textSizes = {
    sm: 'text-sm tracking-brand',
    md: 'text-lg tracking-brand',
    lg: 'text-2xl tracking-brand',
  };

  return (
    <div className={`flex items-center space-x-3 select-none ${className}`}>
      <div className={`relative flex items-center justify-center rounded-xl bg-gradient-to-br from-sky-500/20 to-teal-500/10 border border-sky-500/30 p-1.5 shadow-sm ${iconSizes[size]}`}>
        <svg viewBox="0 0 32 32" fill="none" className="w-full h-full text-sky-400">
          <path 
            d="M4 16C7 16 9 8 12 8C15 8 17 24 20 24C23 24 25 16 28 16" 
            stroke="currentColor" 
            strokeWidth="2.5" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
          />
          <circle cx="12" cy="8" r="2" fill="#38BDF8" />
          <circle cx="20" cy="24" r="2" fill="#2DD4BF" />
        </svg>
      </div>
      {showWordmark && (
        <div className="flex flex-col">
          <span className={`font-semibold text-white tracking-widest uppercase font-mono ${textSizes[size]}`}>
            NUVYRA
          </span>
          <span className="text-[9px] uppercase tracking-wider text-slate-400 font-medium -mt-0.5">
            Health Intelligence
          </span>
        </div>
      )}
    </div>
  );
};