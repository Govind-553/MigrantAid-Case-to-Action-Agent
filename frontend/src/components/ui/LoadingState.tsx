import React from 'react';
import { CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface ProgressStep {
  label: string;
  state: 'pending' | 'active' | 'done';
}

interface LoadingStateProps {
  title?: string;
  description?: string;
  steps?: ProgressStep[];
  className?: string;
}

/**
 * Contextual, staged loading state. Shows what is happening, not a bare spinner.
 */
export const LoadingState: React.FC<LoadingStateProps> = ({
  title = 'Working…',
  description,
  steps,
  className,
}) => {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 sm:p-10 flex flex-col items-center text-center',
        className
      )}
    >
      <div className="relative">
        <div className="h-9 w-9 rounded-full border-2 border-slate-200 dark:border-slate-700 border-t-brand-600 animate-spin" aria-hidden="true" />
      </div>
      <p className="mt-4 text-sm font-semibold text-slate-800 dark:text-slate-200">{title}</p>
      {description && (
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 max-w-sm">{description}</p>
      )}

      {steps && steps.length > 0 && (
        <ul className="mt-5 w-full max-w-xs space-y-2 text-left">
          {steps.map((step, i) => (
            <li
              key={i}
              className="flex items-center gap-2.5 text-xs"
              aria-current={step.state === 'active' ? 'step' : undefined}
            >
              {step.state === 'done' ? (
                <CheckCircle2
                  className="h-4 w-4 text-emerald-500 shrink-0"
                  aria-label="Complete"
                />
              ) : (
                <span
                  className={cn(
                    'flex h-4 w-4 items-center justify-center rounded-full border shrink-0',
                    step.state === 'active'
                      ? 'border-brand-500 border-2 border-t-transparent animate-spin'
                      : 'border-slate-300'
                  )}
                  aria-hidden="true"
                />
              )}
              <span
                className={
                  step.state === 'done'
                    ? 'text-slate-600 dark:text-slate-300'
                    : step.state === 'active'
                    ? 'font-semibold text-slate-800 dark:text-slate-100'
                    : 'text-slate-400 dark:text-slate-500'
                }
              >
                {step.label}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
