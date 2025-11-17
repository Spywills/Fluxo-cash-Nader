import React from 'react';

export const Input = React.forwardRef(({ 
  className = '',
  size = 'md',
  error = false,
  icon: Icon,
  ...props 
}, ref) => {
  const baseStyles = 'w-full rounded-lg border transition-all duration-250 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-4 py-3 text-base',
  };

  const states = error 
    ? 'border-danger-500 focus:ring-danger-500 focus:border-danger-500' 
    : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400';

  return (
    <div className="relative w-full">
      {Icon && <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />}
      <input
        ref={ref}
        className={`${baseStyles} ${sizes[size]} ${states} ${Icon ? 'pl-10' : ''} ${className}`}
        {...props}
      />
    </div>
  );
});

Input.displayName = 'Input';
