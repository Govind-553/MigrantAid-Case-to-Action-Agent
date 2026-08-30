import React, { useState } from 'react';
import { FileCheck, ChevronDown, ChevronUp, ExternalLink, Database, CheckCircle2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { RequirementBadge } from '@/components/ui/RequirementBadge';
import { EmptyState } from '@/components/ui/EmptyState';
import { VerifiedRecommendation } from '@/types';
import { mapRecommendationStatus, mapRequirementState } from '@/lib/status';
import { cn } from '@/lib/cn';

interface RecommendationsViewProps {
  recommendations: VerifiedRecommendation[];
}

export const RecommendationsView: React.FC<RecommendationsViewProps> = ({
  recommendations,
}) => {
  const [expandedId, setExpandedId] = useState<string | null>(
    recommendations.length > 0 ? recommendations[0].resource_id : null
  );

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <Card>
      <SectionHeader
        icon={<FileCheck className="h-5 w-5" />}
        iconTone="success"
        title="Resource Recommendations & Evidence"
        description="Evaluated against approved resource rules. Unknown eligibility is strictly preserved and never converted to eligible."
      />

      {recommendations.length === 0 ? (
        <EmptyState
          icon={<FileCheck className="h-6 w-6" />}
          title="No matching resources yet"
          description="Analyze a case to see relevant resource recommendations, their evidence, and what is still unknown."
        />
      ) : (
        <div className="space-y-3">
          {recommendations.map((rec) => {
            const isExpanded = expandedId === rec.resource_id;
            const status = mapRecommendationStatus(rec.status);
            const supportedReqs = rec.requirement_evaluations.filter(
              (r) => r.status === 'satisfied'
            );
            const unknownReqs = rec.requirement_evaluations.filter(
              (r) => r.status === 'unknown'
            );

            return (
              <div
                key={rec.resource_id}
                className="border border-slate-200 rounded-xl overflow-hidden transition-all bg-white"
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4">
                  <div className="min-w-0 space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-bold text-sm text-slate-900 break-words">
                        {rec.resource_name || rec.resource_id}
                      </span>
                      <span className="text-xs font-mono bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                        {rec.resource_id}
                      </span>
                      <StatusBadge tone={status.tone} icon={status.icon} title={status.title}>
                        {status.label}
                      </StatusBadge>
                    </div>
                    <div className="flex flex-wrap items-center gap-x-2 text-xs text-slate-500">
                      <span className="inline-flex items-center gap-1">
                        <Database className="h-3.5 w-3.5" aria-hidden="true" />
                        Source: {rec.source_id}
                      </span>
                      <span aria-hidden="true">•</span>
                      <span>Dataset: {rec.dataset_version}</span>
                      {rec.human_review_required && (
                        <>
                          <span aria-hidden="true">•</span>
                          <span className="text-warning.text font-semibold">
                            Human review required
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" aria-hidden="true" />
                      {supportedReqs.length} satisfied
                      <span aria-hidden="true">·</span>
                      {unknownReqs.length} unknown
                    </span>
                    <button
                      type="button"
                      onClick={() => toggleExpand(rec.resource_id)}
                      aria-expanded={isExpanded}
                      aria-label={`${isExpanded ? 'Collapse' : 'Expand'} details for ${rec.resource_name || rec.resource_id}`}
                      className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
                    >
                      {isExpanded ? (
                        <ChevronUp className="h-5 w-5" aria-hidden="true" />
                      ) : (
                        <ChevronDown className="h-5 w-5" aria-hidden="true" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Expanded verification + evidence */}
                {isExpanded && (
                  <div className="p-4 sm:p-5 bg-slate-50/60 border-t border-slate-200 space-y-5 animate-fade-in-up">
                    {/* Why it matches / Evidence summary */}
                    {rec.evidence && rec.evidence.length > 0 && (
                      <div>
                        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                          Why it matches
                        </h4>
                        <ul className="space-y-1.5">
                          {rec.evidence.map((ev, i) => (
                            <li
                              key={i}
                              className="flex items-start gap-2 text-xs text-slate-800 bg-white p-2.5 rounded-lg border border-slate-200"
                            >
                              <CheckCircle2
                                className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5"
                                aria-hidden="true"
                              />
                              <span className="min-w-0">
                                <span className="font-medium">{ev.evidence}</span>
                                <span className="text-slate-400 ml-2">
                                  (Source: {ev.source})
                                </span>
                              </span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Requirement verification */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                        Requirement Verification
                      </h4>
                      <div className="space-y-2">
                        {rec.requirement_evaluations.map((req, i) => (
                          <div
                            key={i}
                            className="bg-white p-3 rounded-lg border border-slate-200 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                          >
                            <div className="min-w-0 space-y-1">
                              <div className="flex flex-wrap items-center gap-2">
                                <span className="font-semibold text-slate-900 capitalize">
                                  {req.field.replace(/_/g, ' ')}
                                </span>
                                <span className="text-slate-400 font-mono text-[11px]">
                                  {req.requirement_id}
                                </span>
                              </div>
                              {req.evidence_text && (
                                <p className="text-slate-600">{req.evidence_text}</p>
                              )}
                            </div>
                            <RequirementBadge state={mapRequirementState(req.status)} className="shrink-0" />
                          </div>
                        ))}
                        {rec.requirement_evaluations.length === 0 && (
                          <p className="text-xs text-slate-500 bg-white p-3 rounded-lg border border-slate-200">
                            No requirements evaluated for this resource.
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Missing information */}
                    {rec.missing_information && rec.missing_information.length > 0 && (
                      <div className="p-3.5 bg-warning.bg rounded-lg border border-warning.border text-xs text-slate-800">
                        <span className="font-bold text-warning.text">
                          Information still needed before confirming:
                        </span>
                        <ul className="mt-1.5 space-y-1 list-disc list-inside">
                          {rec.missing_information.map((m, i) => (
                            <li key={i}>{m.replace(/_/g, ' ')}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Verification warnings */}
                    {rec.verification_warnings && rec.verification_warnings.length > 0 && (
                      <div className="p-3.5 bg-white rounded-lg border border-slate-200 text-xs">
                        <span className="font-bold text-slate-700">Verification notes:</span>
                        <ul className="mt-1.5 space-y-1">
                          {rec.verification_warnings.map((w, i) => (
                            <li key={i} className="flex items-start gap-1.5 text-slate-600">
                              <span aria-hidden="true">•</span>
                              <span>
                                {w.message}
                                <span className="text-slate-400 ml-1 uppercase text-[10px]">
                                  {w.code}
                                </span>
                              </span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Source reference */}
                    <div className="flex items-start gap-2 text-[11px] text-slate-500">
                      <ExternalLink className="h-3.5 w-3.5 mt-0.5 shrink-0" aria-hidden="true" />
                      <span className="min-w-0">
                        Referenced from the approved resource knowledge base (source{' '}
                        <span className="font-mono">{rec.source_id}</span>, dataset{' '}
                        <span className="font-mono">{rec.dataset_version}</span>).
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
};
