import React from 'react';
import { cn } from '@/lib/cn';

export type StatusTone = 'neutral' | 'success' | 'warning' | 'danger' | 'info';

interface StatusBadgeProps {
  tone: StatusTone;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  title?: string;
}

const tones: Record<StatusTone, string> = {
  neutral:
    'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-600',
  success:
    'bg-success.bg dark:bg-emerald-950/60 text-success.text dark:text-emerald-300 border-success.border dark:border-emerald-800',
  warning:
    'bg-warning.bg dark:bg-amber-950/50 text-warning.text dark:text-amber-300 border-warning.border dark:border-amber-800',
  danger:
    'bg-danger.bg dark:bg-red-950/50 text-danger.text dark:text-red-300 border-danger.border dark:border-red-800',
  info:
    'bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800',
};

/**
 * Adorned status chip. Always carries an icon + text so that state is
 * never communicated by color alone (WCAG-conscious).
 */
export const StatusBadge: React.FC<StatusBadgeProps> = ({
  tone,
  icon,
  children,
  className,
  title,
}) => {
  return (
    <span
      role="status"
      title={title}
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border whitespace-nowrap',
        tones[tone],
        className
      )}
    >
      {icon && (
        <span aria-hidden="true" className="shrink-0">
          {icon}
        </span>
      )}
      <span>{children}</span>
    </span>
  );
};

/**
 * A small solid dot indicator used inside progress/status elements.
 */
export const StatusDot: React.FC<{ tone: StatusTone; className?: string }> = ({
  tone,
  className,
}) => {
  const colors: Record<StatusTone, string> = {
    neutral: 'bg-slate-400',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-red-500',
    info: 'bg-blue-500',
  };
  return (
    <span
      aria-hidden="true"
      className={cn('inline-block h-2 w-2 rounded-full', colors[tone], className)}
    />
  );
};
