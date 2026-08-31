import React from 'react';
import { ListOrdered, UserCheck, ArrowRight, AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusBadge, StatusTone } from '@/components/ui/StatusBadge';
import { EmptyState } from '@/components/ui/EmptyState';
import { ActionPlan, ActionItem } from '@/types';

interface ActionPlanViewProps {
  actionPlan: ActionPlan;
}

const PRIORITY_META: Record<
  ActionItem['priority'],
  { label: string; tone: StatusTone }
> = {
  critical: { label: 'Critical', tone: 'danger' },
  high: { label: 'High priority', tone: 'warning' },
  medium: { label: 'Standard', tone: 'info' },
  low: { label: 'Low priority', tone: 'neutral' },
};

export const ActionPlanView: React.FC<ActionPlanViewProps> = ({ actionPlan }) => {
  return (
    <Card>
      <SectionHeader
        icon={<ListOrdered className="h-5 w-5" />}
        iconTone="amber"
        title="Sequential Action Plan"
        description="Prioritized, ordered next steps for the caseworker and beneficiary."
      />

      {actionPlan.actions.length === 0 ? (
        <EmptyState
          icon={<ListOrdered className="h-6 w-6" />}
          title="No action plan yet"
          description="An ordered action plan will appear here after the case is analyzed."
        />
      ) : (
        <ol className="space-y-0">
          {actionPlan.actions.map((act) => {
            const meta = PRIORITY_META[act.priority] ?? PRIORITY_META.medium;
            return (
              <li key={act.step} className="relative flex gap-4 pb-5 last:pb-0">
                {/* Connector line */}
                {act.step !== actionPlan.actions.length && (
                  <span
                    className="absolute left-[15px] top-8 bottom-0 w-px bg-slate-200 dark:bg-slate-700"
                    aria-hidden="true"
                  />
                )}

                {/* Step number */}
                <div className="shrink-0">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-white text-sm font-bold shadow-card ring-4 ring-brand-50 dark:ring-brand-950/60">
                    {act.step}
                  </span>
                </div>

                {/* Step content */}
                <div className="min-w-0 flex-1 pt-0.5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-semibold text-slate-900 dark:text-white break-words">
                      {act.action}
                    </span>
                    <StatusBadge tone={meta.tone} className="shrink-0">
                      {meta.label}
                    </StatusBadge>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed mt-1">{act.reason}</p>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 mt-2 text-[11px] text-slate-500 dark:text-slate-400">
                    <div className="flex items-center gap-1">
                      <UserCheck className="h-3.5 w-3.5 text-slate-400 dark:text-slate-500" aria-hidden="true" />
                      <span className="capitalize">
                        {act.responsible_role.replace(/_/g, ' ')}
                      </span>
                    </div>

                    {act.prerequisite && (
                      <div className="flex items-center gap-1">
                        <ArrowRight className="h-3 w-3 text-slate-400 dark:text-slate-500" aria-hidden="true" />
                        <span>Before: {act.prerequisite}</span>
                      </div>
                    )}

                    {act.evidence_reference && (
                      <div className="flex items-center gap-1">
                        <span>Evidence: {act.evidence_reference.replace(/_/g, ' ')}</span>
                      </div>
                    )}
                  </div>

                  {act.unresolved_uncertainty && (
                    <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-warning.bg dark:bg-amber-950/40 border border-warning.border dark:border-amber-800 text-[11px] text-warning.text dark:text-amber-300">
                      <AlertCircle className="h-3.5 w-3.5" aria-hidden="true" />
                      <span>{act.unresolved_uncertainty}</span>
                    </div>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </Card>
  );
};
