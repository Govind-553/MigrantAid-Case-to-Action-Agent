import React from 'react';
import { cn } from '@/lib/cn';

interface SectionHeaderProps {
  icon?: React.ReactNode;
  iconTone?: 'brand' | 'emerald' | 'indigo' | 'amber' | 'slate' | 'violet' | 'success';
  title: string;
  description?: string;
  before?: React.ReactNode;
  after?: React.ReactNode;
  className?: string;
}

const tones = {
  brand: 'bg-brand-50 text-brand-600',
  emerald: 'bg-emerald-50 text-emerald-600',
  indigo: 'bg-indigo-50 text-indigo-600',
  amber: 'bg-amber-50 text-amber-600',
  slate: 'bg-slate-100 text-slate-600',
  violet: 'bg-violet-50 text-violet-600',
  success: 'bg-emerald-50 text-emerald-600',
};

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  icon,
  iconTone = 'brand',
  title,
  description,
  before,
  after,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex items-start justify-between gap-4 mb-4 pb-3 border-b border-slate-100',
        className
      )}
    >
      <div className="flex items-start gap-3 min-w-0">
        {before}
        {icon && (
          <div
            className={cn(
              'p-2 rounded-lg shrink-0',
              tones[iconTone]
            )}
            aria-hidden="true"
          >
            {icon}
          </div>
        )}
        <div className="min-w-0">
          <h3 className="text-base font-semibold text-slate-900 leading-snug">
            {title}
          </h3>
          {description && (
            <p className="text-xs text-slate-500 mt-0.5">{description}</p>
          )}
        </div>
      </div>
      {after && <div className="shrink-0">{after}</div>}
    </div>
  );
};
