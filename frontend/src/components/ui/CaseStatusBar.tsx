import React from 'react';
import { Tag, Target, FileCheck, ListOrdered } from 'lucide-react';
import type { CaseState } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import type { BadgeTone } from '@/components/ui/Badge';

interface CaseStatusBarProps {
  caseState: CaseState;
}

/**
 * Maps raw backend workflow_state values to human-safe display labels and tones.
 *
 * IMPORTANT: 'APPROVED' and 'REFERRALS_APPROVED' must NEVER display as
 * "Approved" in a success/green tone — this would falsely imply eligibility
 * approval. Use amber warning tone and the precise phrase:
 * "Referrals Approved · Eligibility Pending"
 */
function mapWorkflowState(raw: string): { label: string; tone: BadgeTone } {
  const s = raw.toUpperCase();
  switch (s) {
    case 'REFERRALS_APPROVED':
    case 'APPROVED': // legacy value — same safe label
      return { label: 'Referrals Approved · Eligibility Pending', tone: 'warning' };
    case 'MODIFIED':
      return { label: 'Referrals Modified', tone: 'info' };
    case 'MORE_INFORMATION_REQUIRED':
      return { label: 'More Information Required', tone: 'warning' };
    case 'FOLLOW_UP_REQUIRED':
      return { label: 'Follow-up Required', tone: 'warning' };
    case 'ACTION_PLAN_READY':
      return { label: 'Action Plan Ready', tone: 'brand' };
    case 'NEEDS_HUMAN_ATTENTION':
      return { label: 'Needs Human Attention', tone: 'danger' };
    case 'COMPLETED':
      return { label: 'Closed', tone: 'neutral' };
    case 'FAILED':
      return { label: 'Failed', tone: 'danger' };
    default:
      return {
        label: raw.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        tone: 'neutral',
      };
  }
}

export const CaseStatusBar: React.FC<CaseStatusBarProps> = ({ caseState }) => {
  const needs = caseState.needs_assessment?.needs.length ?? 0;
  const recs = caseState.verified_recommendations.length ?? 0;
  const steps = caseState.action_plan?.actions.length ?? 0;

  const { label: statusLabel, tone: statusTone } = mapWorkflowState(caseState.workflow_state);

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
          <Badge tone={statusTone}>
            {statusLabel}
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
