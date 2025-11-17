import React from 'react';

export const Badge = ({ variant = 'default', size = 'md', children, ...props }) => {
  const variants = {
    default: 'bg-gray-100 text-gray-900 border border-gray-200',
    primary: 'bg-primary-100 text-primary-900 border border-primary-300',
    success: 'bg-success-100 text-success-900 border border-success-300',
    danger: 'bg-danger-100 text-danger-900 border border-danger-300',
    warning: 'bg-warning-100 text-warning-900 border border-warning-300',
    'success-solid': 'bg-success-600 text-white',
    'danger-solid': 'bg-danger-600 text-white',
    'warning-solid': 'bg-warning-600 text-white',
  };

  const sizes = {
    sm: 'px-2 py-1 text-xs font-medium',
    md: 'px-3 py-1.5 text-sm font-medium',
    lg: 'px-4 py-2 text-base font-medium',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full ${variants[variant]} ${sizes[size]}`}
      {...props}
    >
      {children}
    </span>
  );
};
