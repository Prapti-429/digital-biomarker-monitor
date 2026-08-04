import React, { createContext, useState, useEffect, useCallback } from 'react';
import { ConnectionStatus, HealthApiResponse } from '../types/api';
import { systemApi } from '../services/api';

interface HealthContextType {
  status: ConnectionStatus;
  timestamp: string | null;
  version: string | null;
  recheckHealth: () => Promise<void>;
}

export const HealthContext = createContext<HealthContextType | undefined>(undefined);

export const HealthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [status, setStatus] = useState<ConnectionStatus>('LOADING');
  const [timestamp, setTimestamp] = useState<string | null>(null);
  const [version, setVersion] = useState<string | null>(null);

  const recheckHealth = useCallback(async () => {
    setStatus('LOADING');
    try {
      const data: HealthApiResponse = await systemApi.getHealth();
      if (data && (data.status === 'OK' || data.status === 'healthy' || data.timestamp)) {
        setStatus('CONNECTED');
        setTimestamp(data.timestamp);
        setVersion(data.version || '1.0.0');
      } else {
        setStatus('UNAVAILABLE');
        setTimestamp(null);
        setVersion(null);
      }
    } catch (error) {
      setStatus('UNAVAILABLE');
      setTimestamp(null);
      setVersion(null);
    }
  }, []);

  useEffect(() => {
    recheckHealth();
  }, [recheckHealth]);

  return (
    <HealthContext.Provider value={{ status, timestamp, version, recheckHealth }}>
      {children}
    </HealthContext.Provider>
  );
};