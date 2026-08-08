/**
 * Health Context Provider.
 *
 * Provides global application health status telemetry and backend connection state.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { systemApi } from '../services/api';

export interface HealthStatus {
  status: string;
  timestamp: string;
  version?: string;
}

export interface HealthContextType {
  health: HealthStatus | null;
  status: string;
  timestamp: string | null;
  version: string;
  isLoading: boolean;
  error: string | null;
  refreshHealth: () => Promise<void>;
  recheckHealth: () => Promise<void>;
}

export const HealthContext = createContext<HealthContextType | undefined>(undefined);

export const HealthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refreshHealth = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await systemApi.getHealthStatus();
      setHealth(data);
    } catch (err: unknown) {
      const errorMessage =
        err && typeof err === 'object' && 'message' in err
          ? String((err as { message: unknown }).message)
          : 'Failed to retrieve system health status.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshHealth();
  }, [refreshHealth]);

  return (
    <HealthContext.Provider
      value={{
        health,
        status: health?.status || (error ? 'offline' : 'connecting'),
        timestamp: health?.timestamp ?? null,
        version: health?.version ?? '1.0.0',
        isLoading,
        error,
        refreshHealth,
        recheckHealth: refreshHealth,
      }}
    >
      {children}
    </HealthContext.Provider>
  );
};

export const useHealth = (): HealthContextType => {
  const context = useContext(HealthContext);
  if (!context) {
    throw new Error('useHealth must be used within a HealthProvider');
  }
  return context;
};