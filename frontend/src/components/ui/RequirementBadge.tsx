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
    className: 'bg-success.bg text-success.text border-success.border',
    icon: <Check className="h-3.5 w-3.5" />,
    title: 'Requirement is satisfied by the available case facts',
  },
  not_satisfied: {
    label: 'Not Satisfied',
    className: 'bg-slate-100 text-slate-700 border-slate-300',
    icon: <X className="h-3.5 w-3.5" />,
    title: 'Requirement is not satisfied',
  },
  unknown: {
    label: 'Unknown',
    className: 'bg-warning.bg text-warning.text border-warning.border',
    icon: <HelpCircle className="h-3.5 w-3.5" />,
    title: 'Not enough evidence — must NOT be treated as satisfied',
  },
  conflict: {
    label: 'Conflict',
    className: 'bg-danger.bg text-danger.text border-danger.border',
    icon: <ShieldAlert className="h-3.5 w-3.5" />,
    title: 'Conflicting case facts detected — human review required',
  },
  not_applicable: {
    label: 'Not Applicable',
    className: 'bg-slate-100 text-slate-500 border-slate-200',
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
