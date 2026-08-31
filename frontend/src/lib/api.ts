import { CaseFact, CaseState, ComparisonReport, HumanReview } from '../types';

/**
 * API base used by the browser.
 *
 * Default is the same-origin relative path `/api`, which is proxied to the
 * backend by the Next.js rewrite in next.config.js (server-side). This keeps
 * the backend URL off the browser and avoids exposing any secrets.
 *
 * NEXT_PUBLIC_API_URL is an optional override for setups that call a backend
 * directly from the browser (in which case backend CORS must allow it).
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

export async function createCase(narrative: string, caseId?: string): Promise<CaseState> {
  const res = await fetch(`${API_BASE}/cases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ narrative, case_id: caseId }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to create case' }));
    throw new Error(error.detail || 'Failed to create case');
  }
  return res.json();
}

export async function getCase(caseId: string): Promise<CaseState> {
  const res = await fetch(`${API_BASE}/cases/${caseId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch case ${caseId}`);
  }
  return res.json();
}

export async function listCases(): Promise<{ cases: any[] }> {
  const res = await fetch(`${API_BASE}/cases`);
  if (!res.ok) {
    throw new Error('Failed to list cases');
  }
  return res.json();
}

export async function updateCaseFacts(caseId: string, facts: CaseFact[]): Promise<CaseState> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/facts`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ facts }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to update facts' }));
    throw new Error(error.detail || 'Failed to update facts');
  }
  return res.json();
}

export async function submitHumanReview(
  caseId: string,
  decision: HumanReview['decision'],
  reviewerNotes?: string,
  modifiedIds?: string[],
  rejectedIds?: string[]
): Promise<CaseState> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      decision,
      reviewer_notes: reviewerNotes,
      modified_recommendation_ids: modifiedIds || [],
      rejected_recommendation_ids: rejectedIds || [],
    }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to submit review' }));
    throw new Error(error.detail || 'Failed to submit review');
  }
  return res.json();
}

export async function getEvaluationComparison(): Promise<ComparisonReport> {
  const res = await fetch(`${API_BASE}/evaluation/comparison`);
  if (!res.ok) {
    throw new Error('Failed to fetch evaluation comparison');
  }
  return res.json();
}
