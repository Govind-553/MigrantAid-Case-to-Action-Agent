export type FactStatus = 'explicit' | 'inferred' | 'unknown' | 'conflicting';

export interface CaseFact {
  field: string;
  value: any;
  status: FactStatus;
  source: string;
  notes?: string | null;
}

export interface Contradiction {
  description: string;
  fact_a: string;
  fact_b: string;
  severity: string;
}

export interface CaseProfile {
  case_id: string;
  narrative: string;
  facts: CaseFact[];
  missing_information: string[];
  contradictions: Contradiction[];
  workflow_state: string;
}

export interface Need {
  category: string;
  priority: 'immediate' | 'high' | 'medium' | 'low';
  reason: string;
  evidence_references: string[];
}

export interface NeedsAssessment {
  case_id: string;
  needs: Need[];
  assessment_notes?: string | null;
}

export interface EvidenceItem {
  case_fact_id: string;
  requirement_id: string;
  result: string;
  evidence: string;
  source: string;
}

export interface RequirementEvaluation {
  requirement_id: string;
  field: string;
  status: 'satisfied' | 'not_satisfied' | 'unknown' | 'conflict' | 'not_applicable';
  case_fact_value?: any;
  required_value?: any;
  evidence_text: string;
}

export interface VerificationWarning {
  code: string;
  message: string;
  severity: 'warning' | 'error' | 'info';
}

export interface VerifiedRecommendation {
  resource_id: string;
  resource_name?: string | null;
  status: 'strong_match' | 'potential_match' | 'insufficient_information' | 'not_supported_by_available_evidence' | 'conflict_detected' | 'no_verified_match';
  evidence: EvidenceItem[];
  requirement_evaluations: RequirementEvaluation[];
  missing_information: string[];
  verification_warnings: VerificationWarning[];
  human_review_required: boolean;
  source_id: string;
  dataset_version: string;
}

export interface ActionItem {
  step: number;
  priority: 'critical' | 'high' | 'medium' | 'low';
  action: string;
  reason: string;
  prerequisite?: string | null;
  responsible_role: string;
  evidence_reference?: string | null;
  unresolved_uncertainty?: string | null;
}

export interface ActionPlan {
  case_id: string;
  actions: ActionItem[];
  plan_notes?: string | null;
}

export interface QualityIssue {
  code: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
  affected_resource_id?: string | null;
}

export interface QualityReport {
  case_id: string;
  passed: boolean;
  issues: QualityIssue[];
  unsupported_claims_detected: boolean;
  missing_evidence_flagged: boolean;
  human_review_enforced: boolean;
  safe_to_present: boolean;
}

export interface HumanReview {
  case_id: string;
  decision: 'pending' | 'approved' | 'modified' | 'rejected' | 'request_information';
  reviewer_notes?: string | null;
  reviewed_at?: string | null;
  modified_recommendation_ids: string[];
  rejected_recommendation_ids: string[];
  follow_up_required: boolean;
}

export interface AgentEvent {
  case_id: string;
  stage: string;
  agent: string;
  event_type: string;
  timestamp: string;
  input_summary?: string | null;
  output_summary?: string | null;
  latency_ms?: number | null;
  retry_count: number;
}

export interface CaseState {
  case_id: string;
  profile?: CaseProfile | null;
  needs_assessment?: NeedsAssessment | null;
  resource_matches: any[];
  verified_recommendations: VerifiedRecommendation[];
  action_plan?: ActionPlan | null;
  quality_report?: QualityReport | null;
  human_review?: HumanReview | null;
  workflow_state: string;
  trajectory: AgentEvent[];
  created_at: string;
  updated_at: string;
}

export interface ComparisonReport {
  dataset_version: string;
  total_cases: number;
  baseline_summary: {
    system: string;
    total_cases: number;
    successful_cases: number;
    varr_percentage: number;
    avg_total_score: number;
    avg_dimension_scores: Record<string, number>;
    failure_category_distribution: Record<string, number>;
    avg_latency_ms: number;
  };
  agentic_summary: {
    system: string;
    total_cases: number;
    successful_cases: number;
    varr_percentage: number;
    avg_total_score: number;
    avg_dimension_scores: Record<string, number>;
    failure_category_distribution: Record<string, number>;
    avg_latency_ms: number;
  };
  improvements: {
    varr_delta_percentage: number;
    score_delta: number;
  };
}
