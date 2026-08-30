import React from 'react';
import { Target, AlertCircle, Clock } from 'lucide-react';
import { NeedsAssessment, Need } from '../types';

interface NeedsViewProps {
  assessment: NeedsAssessment;
}

export const NeedsView: React.FC<NeedsViewProps> = ({ assessment }) => {
  const getPriorityBadge = (priority: Need['priority']) => {
    switch (priority) {
      case 'immediate':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200">
            <AlertCircle className="h-3 w-3" />
            <span>Immediate</span>
          </span>
        );
      case 'high':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
            <Clock className="h-3 w-3" />
            <span>High Priority</span>
          </span>
        );
      case 'medium':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
            <span>Medium Priority</span>
          </span>
        );
      case 'low':
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
            <span>Low Priority</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center space-x-2.5 mb-4 pb-3 border-b border-slate-100">
        <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
          <Target className="h-5 w-5" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-slate-900">Needs Assessment</h3>
          <p className="text-xs text-slate-500">
            Structured needs categorized into controlled vocabulary and prioritized for caseworker intervention.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {assessment.needs.map((need, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-bold text-slate-900 capitalize">
                  {need.category.replace(/_/g, ' ')}
                </span>
              </div>
              {getPriorityBadge(need.priority)}
            </div>

            <p className="text-xs text-slate-700 leading-relaxed mb-2">{need.reason}</p>

            {need.evidence_references && need.evidence_references.length > 0 && (
              <div className="flex items-center space-x-1.5 text-[11px] text-slate-500">
                <span className="font-semibold text-slate-600">Grounded in case facts:</span>
                <div className="flex flex-wrap gap-1">
                  {need.evidence_references.map((ref, i) => (
                    <span key={i} className="bg-white px-1.5 py-0.5 rounded border border-slate-200 text-slate-700">
                      {ref.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
