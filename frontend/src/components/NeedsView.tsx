import React from 'react';
import { Target, AlertCircle, Clock, Info, Zap } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusBadge, StatusTone } from '@/components/ui/StatusBadge';
import { EmptyState } from '@/components/ui/EmptyState';
import { NeedsAssessment, Need } from '@/types';
import { cn } from '@/lib/cn';

interface NeedsViewProps {
  assessment: NeedsAssessment;
}

const PRIORITY_META: Record<
  Need['priority'],
  { label: string; tone: StatusTone; icon: React.ReactNode; ring: string }
> = {
  immediate: {
    label: 'Immediate',
    tone: 'danger',
    icon: <AlertCircle className="h-3.5 w-3.5" />,
    ring: 'border-danger.border dark:border-red-800',
  },
  high: {
    label: 'High priority',
    tone: 'warning',
    icon: <Clock className="h-3.5 w-3.5" />,
    ring: 'border-warning.border dark:border-amber-800',
  },
  medium: {
    label: 'Medium priority',
    tone: 'info',
    icon: <Info className="h-3.5 w-3.5" />,
    ring: 'border-blue-200 dark:border-blue-800',
  },
  low: {
    label: 'Low priority',
    tone: 'neutral',
    icon: <Zap className="h-3.5 w-3.5" />,
    ring: 'border-slate-200 dark:border-slate-700',
  },
};

export const NeedsView: React.FC<NeedsViewProps> = ({ assessment }) => {
  // Visual hierarchy: group by priority rather than a flat colored list
  const sorted = [...assessment.needs].sort((a, b) => {
    const rank = { immediate: 0, high: 1, medium: 2, low: 3 };
    return (rank[a.priority] ?? 4) - (rank[b.priority] ?? 4);
  });

  return (
    <Card>
      <SectionHeader
        icon={<Target className="h-5 w-5" />}
        iconTone="indigo"
        title="Needs Assessment"
        description="Prioritized needs identified from the case facts — ordered by urgency and required intervention."
      />

      {sorted.length === 0 ? (
        <EmptyState
          icon={<Target className="h-6 w-6" />}
          title="No needs identified yet"
          description="Needs will appear here after the case has been analyzed."
        />
      ) : (
        <div className="space-y-2.5">
          {sorted.map((need, idx) => {
            const meta = PRIORITY_META[need.priority] ?? PRIORITY_META.low;
            return (
              <div
                key={idx}
                className={cn(
                  'p-4 rounded-xl border bg-white dark:bg-slate-900 transition-colors',
                  meta.ring
                )}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-sm font-bold text-slate-900 dark:text-white capitalize">
                      {need.category.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <StatusBadge tone={meta.tone} icon={meta.icon}>
                    {meta.label}
                  </StatusBadge>
                </div>

                <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed mt-2">
                  {need.reason}
                </p>

                {need.evidence_references && need.evidence_references.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 mt-3 text-[11px] text-slate-500 dark:text-slate-400">
                    <span className="font-semibold text-slate-600 dark:text-slate-300">Grounded in:</span>
                    {need.evidence_references.map((ref, i) => (
                      <span
                        key={i}
                        className="bg-slate-50 dark:bg-slate-800 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300"
                      >
                        {ref.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
};
