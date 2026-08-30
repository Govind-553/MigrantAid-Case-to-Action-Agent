import React from 'react';
import { Tag, Target, FileCheck, ListOrdered } from 'lucide-react';
import type { CaseState } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';

interface CaseStatusBarProps {
  caseState: CaseState;
}

export const CaseStatusBar: React.FC<CaseStatusBarProps> = ({ caseState }) => {
  const needs = caseState.needs_assessment?.needs.length ?? 0;
  const recs = caseState.verified_recommendations.length ?? 0;
  const steps = caseState.action_plan?.actions.length ?? 0;

  const stats = [
    {
      icon: Target,
      label: 'Needs identified',
      value: needs,
    },
    {
      icon: FileCheck,
      label: 'Recommendations',
      value: recs,
    },
    {
      icon: ListOrdered,
      label: 'Action steps',
      value: steps,
    },
  ];

  return (
    <Card padded={false} className="p-4 sm:p-5">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <Tag className="h-4 w-4 text-slate-400 shrink-0" aria-hidden="true" />
          <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-md">
            {caseState.case_id}
          </span>
          <span className="hidden sm:inline text-xs font-semibold uppercase tracking-wider text-slate-400">
            Workflow status
          </span>
          <Badge tone="success" className="capitalize">
            {caseState.workflow_state.replace(/_/g, ' ')}
          </Badge>
        </div>

        <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
          {stats.map((s) => {
            const Icon = s.icon;
            return (
              <div key={s.label} className="flex items-center gap-2">
                <Icon className="h-3.5 w-3.5 text-slate-400" aria-hidden="true" />
                <span className="text-xs text-slate-600">{s.label}:</span>
                <span className="text-xs font-bold text-slate-900 tabular-nums">
                  {s.value}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};
