import React, { useState } from 'react';
import {
  UserCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  FileQuestion,
  Send,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Field, inputClasses } from '@/components/ui/Field';
import { HumanReview } from '@/types';
import { cn } from '@/lib/cn';

interface HumanReviewViewProps {
  review?: HumanReview | null;
  onSubmitReview: (decision: HumanReview['decision'], notes?: string) => Promise<void>;
  isLoading: boolean;
}

type Decision = HumanReview['decision'];

const DECISIONS: {
  id: Exclude<Decision, 'pending'>;
  label: string;
  description: string;
  icon: React.ReactNode;
  activeClass: string;
  tone: string;
}[] = [
  {
    id: 'approved',
    label: 'Approve',
    description: 'Endorse recommendations and begin referral steps',
    icon: <CheckCircle2 className="h-4 w-4" />,
    activeClass: 'border-emerald-500 bg-emerald-50 text-emerald-900 ring-2 ring-emerald-500/20',
    tone: 'text-emerald-600',
  },
  {
    id: 'modified',
    label: 'Modify',
    description: 'Approve with caseworker modifications',
    icon: <AlertTriangle className="h-4 w-4" />,
    activeClass: 'border-blue-500 bg-blue-50 text-blue-900 ring-2 ring-blue-500/20',
    tone: 'text-blue-600',
  },
  {
    id: 'request_information',
    label: 'Request Info',
    description: 'Hold referrals pending missing answers',
    icon: <FileQuestion className="h-4 w-4" />,
    activeClass: 'border-amber-500 bg-amber-50 text-amber-900 ring-2 ring-amber-500/20',
    tone: 'text-amber-600',
  },
  {
    id: 'rejected',
    label: 'Reject / Close',
    description: 'Reject suggested referrals as unsuitable',
    icon: <XCircle className="h-4 w-4" />,
    activeClass: 'border-rose-500 bg-rose-50 text-rose-900 ring-2 ring-rose-500/20',
    tone: 'text-rose-600',
  },
];

export const HumanReviewView: React.FC<HumanReviewViewProps> = ({
  review,
  onSubmitReview,
  isLoading,
}) => {
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(
    review && review.decision !== 'pending' ? review.decision : null
  );
  const [notes, setNotes] = useState(review?.reviewer_notes || '');

  const isDecided = review && review.decision !== 'pending';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDecision || selectedDecision === 'pending') return;
    await onSubmitReview(selectedDecision, notes);
  };

  return (
    <Card>
      <SectionHeader
        icon={<UserCheck className="h-5 w-5" />}
        iconTone="violet"
        title="Human Review Checkpoint"
        description="MigrantAid assists. You decide. Consequential decisions stay with the caseworker."
        after={
          isDecided && (
            <Badge tone="success">
              <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
              <span className="capitalize">Decision: {review?.decision.replace(/_/g, ' ')}</span>
            </Badge>
          )
        }
      />

      {/* AI vs Human banner */}
      {!isDecided && (
        <div className="mb-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="p-3.5 rounded-lg bg-brand-50 border border-brand-200">
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="h-4 w-4 text-brand-600" aria-hidden="true" />
              <span className="text-xs font-bold text-brand-800 uppercase tracking-wide">
                AI recommendation
              </span>
            </div>
            <p className="text-xs text-brand-900">
              Potentially eligible referrals, prepared with evidence and explicit uncertainty.
              Requires human review.
            </p>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center gap-2 mb-1">
              <ShieldCheck className="h-4 w-4 text-slate-600" aria-hidden="true" />
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                Human decision
              </span>
            </div>
            <p className="text-xs text-slate-600">
              You review the evidence and make the final decision. The system never decides
              eligibility for you.
            </p>
          </div>
        </div>
      )}

      {isDecided ? (
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-600">
            <span className="font-semibold text-slate-900 capitalize">
              Decision recorded: {review?.decision.replace(/_/g, ' ')}
            </span>
            <span>
              Reviewed:{' '}
              {review?.reviewed_at
                ? new Date(review.reviewed_at).toLocaleString()
                : 'N/A'}
            </span>
          </div>
          {review?.modified_recommendation_ids?.length ? (
            <p className="text-xs text-slate-600">
              Modified: {review.modified_recommendation_ids.join(', ')}
            </p>
          ) : null}
          {review?.rejected_recommendation_ids?.length ? (
            <p className="text-xs text-slate-600">
              Rejected: {review.rejected_recommendation_ids.join(', ')}
            </p>
          ) : null}
          {review?.reviewer_notes && (
            <p className="text-xs text-slate-700 bg-white p-3 rounded-lg border border-slate-200">
              <strong className="text-slate-900">Caseworker notes:</strong>{' '}
              {review.reviewer_notes}
            </p>
          )}
          {review?.follow_up_required && (
            <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-amber-700">
              <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
              Follow-up required
            </span>
          )}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-5">
          <fieldset>
            <legend className="block text-xs font-semibold text-slate-700 mb-2">
              Select your decision
            </legend>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
              {DECISIONS.map((d) => {
                const active = selectedDecision === d.id;
                return (
                  <button
                    key={d.id}
                    type="button"
                    onClick={() => setSelectedDecision(d.id)}
                    aria-pressed={active}
                    className={cn(
                      'p-3 rounded-xl border text-left transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
                      active
                        ? d.activeClass
                        : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                    )}
                  >
                    <div className={cn('flex items-center gap-2 mb-1', d.tone)} aria-hidden="true">
                      {d.icon}
                      <span className="font-bold text-xs">{d.label}</span>
                    </div>
                    <p className="text-[11px] text-slate-500">{d.description}</p>
                  </button>
                );
              })}
            </div>
          </fieldset>

          <Field
            label="Caseworker review notes & instructions"
            htmlFor="review-notes"
            hint="Optional"
          >
            <textarea
              id="review-notes"
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add optional notes, instructions for the beneficiary, or rationale for your decision…"
              className={cn(inputClasses, 'resize-y')}
            />
          </Field>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <p className="text-[11px] text-slate-400">
              Recording a decision is a simulation for this prototype — no external action
              is triggered.
            </p>
            <Button
              type="submit"
              size="md"
              loading={isLoading}
              loadingLabel="Recording…"
              disabled={!selectedDecision || selectedDecision === 'pending'}
            >
              <Send className="h-4 w-4" aria-hidden="true" />
              Record Decision
            </Button>
          </div>
        </form>
      )}
    </Card>
  );
};
