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
  neutral: 'bg-slate-100 text-slate-700 border-slate-200',
  brand: 'bg-brand-50 text-brand-700 border-brand-200',
  success: 'bg-success.bg text-success.text border-success.border',
  warning: 'bg-warning.bg text-warning.text border-warning.border',
  danger: 'bg-danger.bg text-danger.text border-danger.border',
  info: 'bg-blue-50 text-blue-700 border-blue-200',
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
