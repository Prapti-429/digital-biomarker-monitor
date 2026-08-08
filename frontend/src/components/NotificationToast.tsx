import React from 'react';
import { useNotification, ToastNotification } from '../contexts/NotificationContext';

export const NotificationToastContainer: React.FC = () => {
  const { toasts, isOnline, removeToast } = useNotification();

  const getToastStyle = (type: ToastNotification['type']) => {
    switch (type) {
      case 'success':
        return 'bg-emerald-50 border-emerald-300 text-emerald-900 icon-emerald';
      case 'warning':
        return 'bg-amber-50 border-amber-300 text-amber-900 icon-amber';
      case 'error':
        return 'bg-rose-50 border-rose-300 text-rose-900 icon-rose';
      case 'info':
      default:
        return 'bg-indigo-50 border-indigo-300 text-indigo-900 icon-indigo';
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col space-y-3 max-w-sm w-full px-4 pointer-events-none">
      {!isOnline && (
        <div className="pointer-events-auto bg-slate-900 text-white border border-slate-700 p-3 rounded-lg shadow-xl flex items-center justify-between text-xs font-medium animate-pulse">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-amber-400"></span>
            <span>Offline Mode Enabled</span>
          </div>
        </div>
      )}

      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto border rounded-xl p-4 shadow-lg transition-all duration-300 transform translate-y-0 ${getToastStyle(
            toast.type
          )} flex items-start justify-between`}
          role="alert"
        >
          <div className="pr-2">
            <h5 className="font-semibold text-sm leading-snug">{toast.title}</h5>
            <p className="text-xs mt-1 opacity-90 leading-relaxed">{toast.message}</p>
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="text-slate-400 hover:text-slate-700 text-sm font-bold ml-2 focus:outline-none"
            aria-label="Close Toast"
          >
            &times;
          </button>
        </div>
      ))}
    </div>
  );
};