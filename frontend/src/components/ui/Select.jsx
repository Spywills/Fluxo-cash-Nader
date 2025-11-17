import React from 'react';

export const Select = React.forwardRef(({ 
  className = '',
  size = 'md',
  error = false,
  options = [],
  ...props 
}, ref) => {
  const baseStyles = 'w-full rounded-lg border transition-all duration-250 focus:outline-none focus:ring-2 focus:ring-offset-2 cursor-pointer';
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-4 py-3 text-base',
  };

  const states = error 
    ? 'border-danger-500 focus:ring-danger-500 focus:border-danger-500' 
    : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400';

  return (
    <select
      ref={ref}
      className={`${baseStyles} ${sizes[size]} ${states} ${className}`}
      {...props}
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
});

Select.displayName = 'Select';
