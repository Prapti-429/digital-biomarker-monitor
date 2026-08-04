import React from 'react';

interface AlertProps {
  title?: string;
  message: string;
  variant?: 'info' | 'success' | 'warning' | 'error';
  action?: React.ReactNode;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  title,
  message,
  variant = 'info',
  action,
  className = '',
}) => {
  const styles = {
    info: 'bg-blue-50 text-blue-800 border-blue-200',
    success: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    warning: 'bg-amber-50 text-amber-800 border-amber-200',
    error: 'bg-red-50 text-red-800 border-red-200',
  };

  return (
    <div className={`p-4 border rounded-md role="alert" ${styles[variant]} ${className}`}>
      <div className="flex items-start justify-between space-x-3">
        <div className="flex-1">
          {title && <h5 className="font-semibold text-sm mb-1">{title}</h5>}
          <p className="text-xs leading-relaxed">{message}</p>
        </div>
        {action && <div className="flex-shrink-0 text-xs">{action}</div>}
      </div>
    </div>
  );
};