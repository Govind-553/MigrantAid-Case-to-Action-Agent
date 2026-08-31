import React from 'react';
import { Check, X, HelpCircle, ShieldAlert, Minus } from 'lucide-react';
import { cn } from '@/lib/cn';

export type RequirementState =
  | 'satisfied'
  | 'not_satisfied'
  | 'unknown'
  | 'conflict'
  | 'not_applicable';

const config: Record<
  RequirementState,
  { label: string; className: string; icon: React.ReactNode; title: string }
> = {
  satisfied: {
    label: 'Satisfied',
    className:
      'bg-success.bg dark:bg-emerald-950/60 text-success.text dark:text-emerald-300 border-success.border dark:border-emerald-800',
    icon: <Check className="h-3.5 w-3.5" />,
    title: 'Requirement is satisfied by the available case facts',
  },
  not_satisfied: {
    label: 'Not Satisfied',
    className:
      'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-600',
    icon: <X className="h-3.5 w-3.5" />,
    title: 'Requirement is not satisfied',
  },
  unknown: {
    label: 'Unknown',
    className:
      'bg-warning.bg dark:bg-amber-950/50 text-warning.text dark:text-amber-300 border-warning.border dark:border-amber-800',
    icon: <HelpCircle className="h-3.5 w-3.5" />,
    title: 'Not enough evidence — must NOT be treated as satisfied',
  },
  conflict: {
    label: 'Conflict',
    className:
      'bg-danger.bg dark:bg-red-950/50 text-danger.text dark:text-red-300 border-danger.border dark:border-red-800',
    icon: <ShieldAlert className="h-3.5 w-3.5" />,
    title: 'Conflicting case facts detected — human review required',
  },
  not_applicable: {
    label: 'Not Applicable',
    className:
      'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700',
    icon: <Minus className="h-3.5 w-3.5" />,
    title: 'Requirement does not apply to this case',
  },
};

interface RequirementBadgeProps {
  state: RequirementState;
  className?: string;
}

/**
 * Explicit, icon + label verification state chip.
 * UNKNOWN is visually and semantically distinct from SATISFIED.
 */
export const RequirementBadge: React.FC<RequirementBadgeProps> = ({
  state,
  className,
}) => {
  const c = config[state] ?? config.not_applicable;
  return (
    <span
      role="status"
      title={c.title}
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs font-semibold border whitespace-nowrap',
        c.className,
        className
      )}
    >
      <span aria-hidden="true">{c.icon}</span>
      <span>{c.label}</span>
    </span>
  );
};
