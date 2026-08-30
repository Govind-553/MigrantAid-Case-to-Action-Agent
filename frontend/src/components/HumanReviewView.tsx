import React, { useState } from 'react';
import { UserCheck, CheckCircle2, AlertTriangle, XCircle, FileQuestion, Send, Check } from 'lucide-react';
import { HumanReview } from '../types';

interface HumanReviewViewProps {
  review?: HumanReview | null;
  onSubmitReview: (decision: HumanReview['decision'], notes?: string) => Promise<void>;
  isLoading: boolean;
}

export const HumanReviewView: React.FC<HumanReviewViewProps> = ({
  review,
  onSubmitReview,
  isLoading,
}) => {
  const [selectedDecision, setSelectedDecision] = useState<HumanReview['decision']>('approved');
  const [notes, setNotes] = useState(review?.reviewer_notes || '');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmitReview(selectedDecision, notes);
  };

  const isDecided = review && review.decision !== 'pending';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
            <UserCheck className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-900">Human-in-the-Loop Review Checkpoint</h3>
            <p className="text-xs text-slate-500">
              Caseworkers maintain ultimate authority over referrals and action plan execution.
            </p>
          </div>
        </div>

        {isDecided && (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span className="capitalize">Decision: {review.decision}</span>
          </span>
        )}
      </div>

      {isDecided ? (
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-600">
            <span className="font-semibold text-slate-900">Review Status: Completed</span>
            <span>Reviewed At: {review.reviewed_at ? new Date(review.reviewed_at).toLocaleString() : 'N/A'}</span>
          </div>
          {review.reviewer_notes && (
            <p className="text-xs text-slate-700 bg-white p-3 rounded-lg border border-slate-200">
              <strong className="text-slate-900">Caseworker Notes:</strong> {review.reviewer_notes}
            </p>
          )}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Select Caseworker Action:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
              <button
                type="button"
                onClick={() => setSelectedDecision('approved')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  selectedDecision === 'approved'
                    ? 'border-emerald-500 bg-emerald-50 text-emerald-900 ring-2 ring-emerald-500/20'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2 mb-1">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  <span className="font-bold text-xs">Approve Plan</span>
                </div>
                <p className="text-[11px] text-slate-500">Endorse recommendations and begin referral steps</p>
              </button>

              <button
                type="button"
                onClick={() => setSelectedDecision('modified')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  selectedDecision === 'modified'
                    ? 'border-blue-500 bg-blue-50 text-blue-900 ring-2 ring-blue-500/20'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2 mb-1">
                  <AlertTriangle className="h-4 w-4 text-blue-600" />
                  <span className="font-bold text-xs">Modify Plan</span>
                </div>
                <p className="text-[11px] text-slate-500">Approve with caseworker modifications or adjustments</p>
              </button>

              <button
                type="button"
                onClick={() => setSelectedDecision('request_information')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  selectedDecision === 'request_information'
                    ? 'border-amber-500 bg-amber-50 text-amber-900 ring-2 ring-amber-500/20'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2 mb-1">
                  <FileQuestion className="h-4 w-4 text-amber-600" />
                  <span className="font-bold text-xs">Request Info</span>
                </div>
                <p className="text-[11px] text-slate-500">Hold referrals pending answers to missing questions</p>
              </button>

              <button
                type="button"
                onClick={() => setSelectedDecision('rejected')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  selectedDecision === 'rejected'
                    ? 'border-rose-500 bg-rose-50 text-rose-900 ring-2 ring-rose-500/20'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2 mb-1">
                  <XCircle className="h-4 w-4 text-rose-600" />
                  <span className="font-bold text-xs">Reject / Close</span>
                </div>
                <p className="text-[11px] text-slate-500">Reject suggested referrals as unsuitable for case</p>
              </button>
            </div>
          </div>

          <div>
            <label htmlFor="notes" className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
              Caseworker Review Notes & Instructions:
            </label>
            <textarea
              id="notes"
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add optional notes, instructions for the beneficiary, or rationale for modification..."
              className="w-full px-3 py-2 text-xs text-slate-800 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className="inline-flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-medium px-4 py-2 rounded-lg shadow-sm transition-all disabled:opacity-50"
            >
              <Send className="h-3.5 w-3.5" />
              <span>Record Caseworker Decision</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
