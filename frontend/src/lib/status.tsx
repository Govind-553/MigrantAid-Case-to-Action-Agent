import {
  CheckCircle2,
  HelpCircle,
  AlertTriangle,
  AlertOctagon,
  MinusCircle,
} from 'lucide-react';
import type { FactStatus } from '@/types';
import type { StatusTone } from '@/components/ui/StatusBadge';
import type { RequirementState } from '@/components/ui/RequirementBadge';

export interface FactStatusModel {
  label: string;
  tone: StatusTone;
  icon: React.ReactNode;
  title: string;
}

export const FACT_STATUS_MODEL: Record<FactStatus, FactStatusModel> = {
  explicit: {
    label: 'Explicit',
    tone: 'success',
    icon: <CheckCircle2 className="h-3.5 w-3.5" />,
    title: 'Explicitly stated in the case narrative',
  },
  inferred: {
    label: 'Inferred',
    tone: 'info',
    icon: <HelpCircle className="h-3.5 w-3.5" />,
    title: 'Inferred from the case narrative',
  },
  conflicting: {
    label: 'Conflicting',
    tone: 'danger',
    icon: <AlertOctagon className="h-3.5 w-3.5" />,
    title: 'Conflicting statements detected — human review required',
  },
  unknown: {
    label: 'Unknown',
    tone: 'warning',
    icon: <AlertTriangle className="h-3.5 w-3.5" />,
    title: 'Not enough information to determine this fact',
  },
};

export function mapFactStatus(status: FactStatus): FactStatusModel {
  return FACT_STATUS_MODEL[status] ?? FACT_STATUS_MODEL.unknown;
}

export function mapRequirementState(status: string): RequirementState {
  switch (status) {
    case 'satisfied':
      return 'satisfied';
    case 'not_satisfied':
      return 'not_satisfied';
    case 'unknown':
      return 'unknown';
    case 'conflict':
      return 'conflict';
    default:
      return 'not_applicable';
  }
}

/** Categorize a verified recommendation's status for display. */
export interface RecommendationStatusModel {
  label: string;
  tone: StatusTone;
  icon: React.ReactNode;
  title: string;
}

const RECOMMENDATION_STATUS_MODEL: Record<string, RecommendationStatusModel> = {
  strong_match: {
    label: 'Verified Match',
    tone: 'success',
    icon: <CheckCircle2 className="h-3.5 w-3.5" />,
    title: 'Requirements appear consistent with available case facts',
  },
  potential_match: {
    label: 'Potential Match',
    tone: 'warning',
    icon: <HelpCircle className="h-3.5 w-3.5" />,
    title: 'May be relevant, but more evidence is needed before confirming',
  },
  insufficient_information: {
    label: 'Insufficient Information',
    tone: 'info',
    icon: <AlertTriangle className="h-3.5 w-3.5" />,
    title: 'Not enough information to confirm relevance',
  },
  conflict_detected: {
    label: 'Conflict Detected',
    tone: 'danger',
    icon: <AlertOctagon className="h-3.5 w-3.5" />,
    title: 'Conflicting facts — human review required',
  },
  not_supported_by_available_evidence: {
    label: 'Not Supported',
    tone: 'neutral',
    icon: <MinusCircle className="h-3.5 w-3.5" />,
    title: 'Not supported by the available evidence',
  },
  no_verified_match: {
    label: 'No Verified Match',
    tone: 'neutral',
    icon: <MinusCircle className="h-3.5 w-3.5" />,
    title: 'No verified match from the approved dataset',
  },
};

export function mapRecommendationStatus(status: string): RecommendationStatusModel {
  return (
    RECOMMENDATION_STATUS_MODEL[status] ?? {
      label: (status ?? '').replace(/_/g, ' '),
      tone: 'neutral',
      icon: <MinusCircle className="h-3.5 w-3.5" />,
      title: status,
    }
  );
}
