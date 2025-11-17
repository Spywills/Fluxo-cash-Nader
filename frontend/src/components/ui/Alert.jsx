import React from 'react';
import { AlertCircle, CheckCircle, AlertTriangle, Info, X } from 'lucide-react';

export const Alert = ({ variant = 'info', title, description, onClose, className = '', ...props }) => {
  const variants = {
    info: 'bg-blue-50 border-blue-200 text-blue-900',
    success: 'bg-green-50 border-green-200 text-green-900',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    danger: 'bg-red-50 border-red-200 text-red-900',
  };

  const iconVariants = {
    info: <Info className="h-5 w-5 text-blue-600" />,
    success: <CheckCircle className="h-5 w-5 text-green-600" />,
    warning: <AlertTriangle className="h-5 w-5 text-yellow-600" />,
    danger: <AlertCircle className="h-5 w-5 text-red-600" />,
  };

  return (
    <div className={`rounded-lg border p-4 flex gap-4 animate-slide-in ${variants[variant]} ${className}`} {...props}>
      <div className="flex-shrink-0">
        {iconVariants[variant]}
      </div>
      <div className="flex-1">
        {title && <h4 className="font-semibold text-sm mb-1">{title}</h4>}
        {description && <p className="text-sm opacity-90">{description}</p>}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity"
        >
          <X className="h-5 w-5" />
        </button>
      )}
    </div>
  );
};

export const AlertTitle = ({ children, ...props }) => (
  <h4 className="font-semibold text-sm mb-1" {...props}>{children}</h4>
);

export const AlertDescription = ({ children, ...props }) => (
  <p className="text-sm opacity-90" {...props}>{children}</p>
);
