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
  neutral: 'bg-slate-100 text-slate-700 border-slate-300',
  success: 'bg-success.bg text-success.text border-success.border',
  warning: 'bg-warning.bg text-warning.text border-warning.border',
  danger: 'bg-danger.bg text-danger.text border-danger.border',
  info: 'bg-blue-50 text-blue-700 border-blue-200',
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
