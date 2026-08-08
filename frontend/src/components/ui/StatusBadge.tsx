import React from 'react';
export type ConnectionStatus = 'online' | 'offline' | 'connecting' | 'LOADING' | 'UNKNOWN' | string;

export interface StatusBadgeProps {
  status: ConnectionStatus;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const getStatusStyles = (s: string) => {
    switch (s?.toLowerCase()) {
      case 'online':
      case 'connected':
      case 'healthy':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'connecting':
      case 'loading':
        return 'bg-amber-100 text-amber-800 border-amber-300 animate-pulse';
      case 'offline':
      case 'error':
      default:
        return 'bg-rose-100 text-rose-800 border-rose-300';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border uppercase tracking-wider ${getStatusStyles(
        status
      )} ${className}`}
    >
      <span className="h-1.5 w-1.5 mr-1.5 rounded-full bg-current"></span>
      {status || 'OFFLINE'}
    </span>
  );
};