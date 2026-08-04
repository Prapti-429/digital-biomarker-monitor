import React from 'react';
import { ConnectionStatus } from '../../types/api';

interface StatusBadgeProps {
  status: ConnectionStatus;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const configurations = {
    LOADING: 'bg-slate-100 text-slate-700 border-slate-200 animate-pulse',
    CONNECTED: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    UNAVAILABLE: 'bg-red-100 text-red-800 border-red-200',
  };

  const labels = {
    LOADING: 'Verifying System Node...',
    CONNECTED: 'Platform Active',
    UNAVAILABLE: 'Data Node Offline',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${configurations[status]}`}>
      <span className={`h-1.5 w-1.5 rounded-full mr-1.5 ${
        status === 'CONNECTED' ? 'bg-emerald-500' : status === 'UNAVAILABLE' ? 'bg-red-500' : 'bg-slate-400'
      }`} />
      {labels[status]}
    </span>
  );
};