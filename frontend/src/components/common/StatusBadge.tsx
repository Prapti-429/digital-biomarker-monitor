import React from 'react';

export type StatusVariant = 'stable' | 'improving' | 'variation' | 'alert' | 'neutral';

interface StatusBadgeProps {
  status: StatusVariant | string;
  label?: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, size = 'md' }) => {
  const normalized = status.toLowerCase();

  const configs: Record<string, { bg: string; dot: string; defaultLabel: string }> = {
    stable: {
      bg: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
      dot: 'bg-emerald-400',
      defaultLabel: 'Within baseline',
    },
    improving: {
      bg: 'bg-teal-500/10 border-teal-500/20 text-teal-300',
      dot: 'bg-teal-400',
      defaultLabel: 'Improving',
    },
    variation: {
      bg: 'bg-amber-500/10 border-amber-500/20 text-amber-300',
      dot: 'bg-amber-400',
      defaultLabel: 'Baseline variation',
    },
    alert: {
      bg: 'bg-rose-500/10 border-rose-500/20 text-rose-400',
      dot: 'bg-rose-400',
      defaultLabel: 'Attention needed',
    },
    neutral: {
      bg: 'bg-slate-800 border-slate-700 text-slate-300',
      dot: 'bg-slate-400',
      defaultLabel: 'Monitoring',
    },
  };

  const config = configs[normalized] ?? configs.neutral;
  const displayText = label ?? config.defaultLabel;
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${config.bg} ${sizeClasses}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot} animate-pulse`} />
      {displayText}
    </span>
  );
};