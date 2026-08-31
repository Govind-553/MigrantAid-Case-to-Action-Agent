import type { CaseState } from '@/types';

export type WorkflowStageId =
  | 'intake'
  | 'facts'
  | 'needs'
  | 'resources'
  | 'verification'
  | 'action-plan'
  | 'review'
  | 'trajectory';

export interface WorkflowStage {
  id: WorkflowStageId;
  label: string;
  shortLabel: string;
  description: string;
}

export const WORKFLOW_STAGES: WorkflowStage[] = [
  {
    id: 'intake',
    label: 'Case Intake',
    shortLabel: 'Intake',
    description: 'Enter the beneficiary situation',
  },
  {
    id: 'facts',
    label: 'Facts',
    shortLabel: 'Facts',
    description: 'Review extracted structured facts',
  },
  {
    id: 'needs',
    label: 'Needs',
    shortLabel: 'Needs',
    description: 'Prioritized needs assessment',
  },
  {
    id: 'resources',
    label: 'Resources',
    shortLabel: 'Resources',
    description: 'Matching resource recommendations',
  },
  {
    id: 'verification',
    label: 'Verification',
    shortLabel: 'Verify',
    description: 'Evidence & requirement verification',
  },
  {
    id: 'action-plan',
    label: 'Action Plan',
    shortLabel: 'Actions',
    description: 'Sequential caseworker actions',
  },
  {
    id: 'review',
    label: 'Human Review',
    shortLabel: 'Review',
    description: 'Human decision checkpoint',
  },
  {
    id: 'trajectory',
    label: 'Trajectory',
    shortLabel: 'Trajectory',
    description: 'How MigrantAid reached this result',
  },
];

/** Returns which workflow stages currently have data in the case state. */
export function getAvailableStages(caseState: CaseState | null): Set<WorkflowStageId> {
  const available = new Set<WorkflowStageId>(['intake']);
  if (!caseState) return available;

  if (caseState.profile && caseState.profile.facts.length > 0) available.add('facts');
  if (caseState.needs_assessment && caseState.needs_assessment.needs.length > 0)
    available.add('needs');
  if (caseState.verified_recommendations.length > 0) available.add('resources');
  if (
    caseState.verified_recommendations.some(
      (r) => r.requirement_evaluations && r.requirement_evaluations.length > 0
    )
  )
    available.add('verification');
  if (caseState.action_plan && caseState.action_plan.actions.length > 0)
    available.add('action-plan');
  if (caseState.human_review) available.add('review');
  if (caseState.trajectory && caseState.trajectory.length > 0) available.add('trajectory');

  return available;
}

/** Best initial stage to show once a case exists. */
export function getInitialStage(caseState: CaseState | null): WorkflowStageId {
  if (!caseState) return 'intake';
  const available = getAvailableStages(caseState);
  const order: WorkflowStageId[] = [
    'intake',
    'facts',
    'needs',
    'resources',
    'verification',
    'action-plan',
    'review',
    'trajectory',
  ];
  for (const id of order) {
    if (available.has(id)) return id;
  }
  return 'intake';
}

/** Whether an earlier stage exists that this stage depends on (for gating). */
export function isStageUnlocked(
  stage: WorkflowStageId,
  available: Set<WorkflowStageId>
): boolean {
  if (stage === 'intake') return true;
  return available.has(stage);
}
