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
  brand: 'bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-300',
  emerald: 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-300',
  indigo: 'bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-300',
  amber: 'bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-300',
  slate: 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300',
  violet: 'bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-300',
  success: 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-300',
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
        'flex items-start justify-between gap-4 mb-4 pb-3 border-b border-slate-100 dark:border-slate-800',
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
          <h3 className="text-base font-semibold text-slate-900 dark:text-white leading-snug">
            {title}
          </h3>
          {description && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{description}</p>
          )}
        </div>
      </div>
      {after && <div className="shrink-0">{after}</div>}
    </div>
  );
};
