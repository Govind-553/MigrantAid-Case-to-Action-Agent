import React from 'react';
import {
  FileText,
  ClipboardList,
  Target,
  FileCheck,
  ShieldCheck,
  ListOrdered,
  UserCheck,
  Activity,
  Check,
} from 'lucide-react';
import type { WorkflowStageId } from '@/lib/workflow';
import { WORKFLOW_STAGES } from '@/lib/workflow';
import { cn } from '@/lib/cn';

const STAGE_ICONS: Record<WorkflowStageId, React.ReactNode> = {
  intake: <FileText className="h-4 w-4" />,
  facts: <ClipboardList className="h-4 w-4" />,
  needs: <Target className="h-4 w-4" />,
  resources: <FileCheck className="h-4 w-4" />,
  verification: <ShieldCheck className="h-4 w-4" />,
  'action-plan': <ListOrdered className="h-4 w-4" />,
  review: <UserCheck className="h-4 w-4" />,
  trajectory: <Activity className="h-4 w-4" />,
};

interface WorkflowNavProps {
  activeStage: WorkflowStageId;
  available: Set<WorkflowStageId>;
  onSelect: (stage: WorkflowStageId) => void;
}

/**
 * Workflow navigation. Shows the ordered case workflow and clearly
 * communicates where the user is. Renders a vertical stepper on desktop
 * and a horizontal scrollable strip on smaller screens.
 */
export const WorkflowNav: React.FC<WorkflowNavProps> = ({
  activeStage,
  available,
  onSelect,
}) => {
  const order = WORKFLOW_STAGES.map((s) => s.id);

  return (
    <nav aria-label="Case workflow">
      {/* Mobile horizontal strip */}
      <div className="lg:hidden -mx-4 px-4 sm:-mx-6 sm:px-6 overflow-x-auto pb-2">
        <ol className="flex gap-1.5 min-w-max">
          {WORKFLOW_STAGES.map((stage) => {
            const isActive = activeStage === stage.id;
            const unlocked = available.has(stage.id) || stage.id === 'intake';
            const idx = order.indexOf(stage.id);
            const prevIdx = order.indexOf(activeStage);
            const isReached = idx <= prevIdx && unlocked;
            return (
              <li key={stage.id}>
                <button
                  type="button"
                  onClick={() => unlocked && onSelect(stage.id)}
                  disabled={!unlocked}
                  aria-current={isActive ? 'page' : undefined}
                  aria-disabled={!unlocked}
                  className={cn(
                    'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border whitespace-nowrap transition-colors',
                    isActive
                      ? 'bg-brand-600 text-white border-brand-600 shadow-card'
                      : unlocked && isReached
                      ? 'bg-white text-brand-700 border-slate-200 hover:bg-brand-50'
                      : unlocked
                      ? 'bg-white text-slate-600 border-slate-200 hover:bg-brand-50'
                      : 'bg-slate-50 text-slate-400 border-slate-200 cursor-not-allowed'
                  )}
                >
                  <span aria-hidden="true">{STAGE_ICONS[stage.id]}</span>
                  {stage.label}
                </button>
              </li>
            );
          })}
        </ol>
      </div>

      {/* Desktop vertical stepper */}
      <ol className="hidden lg:flex flex-col gap-1">
        {WORKFLOW_STAGES.map((stage) => {
          const isActive = activeStage === stage.id;
          const isLocked = !available.has(stage.id) && stage.id !== 'intake';
          const isDone =
            available.has(stage.id) &&
            stage.id !== 'intake' &&
            order.indexOf(stage.id) < order.indexOf(activeStage);
          return (
            <li key={stage.id}>
              <button
                type="button"
                onClick={() => !isLocked && onSelect(stage.id)}
                disabled={isLocked}
                aria-current={isActive ? 'page' : undefined}
                className={cn(
                  'w-full flex items-center gap-3 rounded-lg px-3 py-2 text-left text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
                  isActive
                    ? 'bg-brand-50 text-brand-800 ring-1 ring-brand-200'
                    : isLocked
                    ? 'text-slate-400 cursor-not-allowed'
                    : 'text-slate-600 hover:bg-slate-50'
                )}
              >
                <span
                  className={cn(
                    'flex h-6 w-6 shrink-0 items-center justify-center rounded-full border',
                    isActive
                      ? 'bg-brand-600 text-white border-brand-600'
                      : isDone
                      ? 'bg-emerald-50 text-emerald-600 border-emerald-300'
                      : isLocked
                      ? 'bg-slate-50 text-slate-300 border-slate-200'
                      : 'bg-white text-slate-400 border-slate-300'
                  )}
                >
                  {isDone ? (
                    <Check className="h-3.5 w-3.5" aria-hidden="true" />
                  ) : (
                    <span aria-hidden="true">{STAGE_ICONS[stage.id]}</span>
                  )}
                </span>
                <span className="truncate">{stage.label}</span>
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
