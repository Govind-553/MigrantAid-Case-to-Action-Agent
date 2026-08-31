import React from 'react';
import { cn } from '@/lib/cn';

export type BadgeTone =
  | 'neutral'
  | 'brand'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info';

interface BadgeProps {
  tone?: BadgeTone;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  title?: string;
}

const tones: Record<BadgeTone, string> = {
  neutral:
    'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-600',
  brand:
    'bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 border-brand-200 dark:border-brand-800',
  success:
    'bg-success.bg dark:bg-emerald-950/60 text-success.text dark:text-emerald-300 border-success.border dark:border-emerald-800',
  warning:
    'bg-warning.bg dark:bg-amber-950/50 text-warning.text dark:text-amber-300 border-warning.border dark:border-amber-800',
  danger:
    'bg-danger.bg dark:bg-red-950/50 text-danger.text dark:text-red-300 border-danger.border dark:border-red-800',
  info:
    'bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800',
};

export const Badge: React.FC<BadgeProps> = ({
  tone = 'neutral',
  icon,
  children,
  className,
  title,
}) => {
  return (
    <span
      title={title}
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border whitespace-nowrap',
        tones[tone],
        className
      )}
    >
      {icon && <span aria-hidden="true">{icon}</span>}
      {children}
    </span>
  );
};
