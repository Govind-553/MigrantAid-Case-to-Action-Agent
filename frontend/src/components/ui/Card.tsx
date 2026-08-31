import React from 'react';
import { cn } from '@/lib/cn';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padded?: boolean;
}

export const Card: React.FC<CardProps> = ({
  padded = true,
  className,
  children,
  ...rest
}) => {
  return (
    <div
      className={cn(
        'bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-card',
        padded && 'p-5 sm:p-6',
        className
      )}
      {...rest}
    >
      {children}
    </div>
  );
};
