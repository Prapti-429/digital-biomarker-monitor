import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export type NotificationType = 'success' | 'warning' | 'error' | 'info';

export interface ToastNotification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  duration?: number;
}

interface NotificationContextType {
  toasts: ToastNotification[];
  isOnline: boolean;
  showToast: (type: NotificationType, title: string, message: string, duration?: number) => void;
  removeToast: (id: string) => void;
  clearAllToasts: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastNotification[]>([]);
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback(
    (type: NotificationType, title: string, message: string, duration = 5000) => {
      const id = `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      const newToast: ToastNotification = { id, type, title, message, duration };

      setToasts((prev) => [...prev.slice(-4), newToast]); // Keep max 5 active toasts

      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }
    },
    [removeToast]
  );

  const clearAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  // Online / Offline Network Monitoring
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      showToast('success', 'Network Reconnected', 'You are back online. Syncing data...', 4000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      showToast('warning', 'Network Disconnected', 'Working offline. Pending requests will retry on reconnect.', 0);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [showToast]);

  return (
    <NotificationContext.Provider
      value={{
        toasts,
        isOnline,
        showToast,
        removeToast,
        clearAllToasts,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotification = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};