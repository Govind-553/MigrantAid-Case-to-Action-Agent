import React, { useState } from 'react';
import {
  CheckCircle,
  AlertCircle,
  HelpCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  FileCheck,
  ShieldAlert,
  ExternalLink,
} from 'lucide-react';
import { VerifiedRecommendation, RequirementEvaluation } from '../types';

interface RecommendationsViewProps {
  recommendations: VerifiedRecommendation[];
}

export const RecommendationsView: React.FC<RecommendationsViewProps> = ({ recommendations }) => {
  const [expandedId, setExpandedId] = useState<string | null>(
    recommendations.length > 0 ? recommendations[0].resource_id : null
  );

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getStatusBadge = (status: VerifiedRecommendation['status']) => {
    switch (status) {
      case 'strong_match':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle className="h-3.5 w-3.5 text-emerald-600" />
            <span>Strong Match (Verified)</span>
          </span>
        );
      case 'potential_match':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300">
            <HelpCircle className="h-3.5 w-3.5 text-amber-600" />
            <span>Potential Match</span>
          </span>
        );
      case 'insufficient_information':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300">
            <AlertCircle className="h-3.5 w-3.5 text-blue-600" />
            <span>Insufficient Information</span>
          </span>
        );
      case 'conflict_detected':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300">
            <ShieldAlert className="h-3.5 w-3.5 text-rose-600" />
            <span>Conflict Detected</span>
          </span>
        );
      case 'not_supported_by_available_evidence':
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-300">
            <XCircle className="h-3.5 w-3.5 text-slate-500" />
            <span>Not Supported</span>
          </span>
        );
    }
  };

  const getReqStatusBadge = (status: RequirementEvaluation['status']) => {
    switch (status) {
      case 'satisfied':
        return <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">Satisfied</span>;
      case 'unknown':
        return <span className="text-[11px] font-bold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">Unknown (Needs Evidence)</span>;
      case 'conflict':
        return <span className="text-[11px] font-bold text-rose-700 bg-rose-50 px-1.5 py-0.5 rounded border border-rose-200">Conflict</span>;
      case 'not_satisfied':
      default:
        return <span className="text-[11px] font-bold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">Not Satisfied</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
            <FileCheck className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-900">Verified Recommendations & Evidence</h3>
            <p className="text-xs text-slate-500">
              Evaluated against approved resource rules. Unknown eligibility is strictly preserved, never converted to eligible.
            </p>
          </div>
        </div>
      </div>

      {recommendations.length === 0 ? (
        <p className="text-xs text-slate-500 italic p-4 text-center">No matching resources retrieved for this case.</p>
      ) : (
        <div className="space-y-3">
          {recommendations.map((rec) => {
            const isExpanded = expandedId === rec.resource_id;

            return (
              <div
                key={rec.resource_id}
                className="border border-slate-200 rounded-xl overflow-hidden transition-all bg-white"
              >
                {/* Header Card */}
                <div
                  onClick={() => toggleExpand(rec.resource_id)}
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50/70 transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2.5">
                      <span className="font-bold text-sm text-slate-900">
                        {rec.resource_name || rec.resource_id}
                      </span>
                      <span className="text-xs font-mono bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                        {rec.resource_id}
                      </span>
                      {getStatusBadge(rec.status)}
                    </div>
                    <p className="text-xs text-slate-500 flex items-center space-x-2">
                      <span>Source: {rec.source_id}</span>
                      <span>•</span>
                      <span>Dataset Version: {rec.dataset_version}</span>
                    </p>
                  </div>

                  <div className="text-slate-400">
                    {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="p-4 bg-slate-50/50 border-t border-slate-200 space-y-4">
                    {/* Requirement-by-Requirement Table */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                        Deterministic Requirement Check:
                      </h4>
                      <div className="space-y-2">
                        {rec.requirement_evaluations.map((req, i) => (
                          <div
                            key={i}
                            className="bg-white p-3 rounded-lg border border-slate-200 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                          >
                            <div className="space-y-1">
                              <div className="flex items-center space-x-2">
                                <span className="font-semibold text-slate-900 capitalize">
                                  {req.field.replace(/_/g, ' ')}
                                </span>
                                <span className="text-slate-400">|</span>
                                <span className="text-slate-600 font-mono text-[11px]">
                                  Req ID: {req.requirement_id}
                                </span>
                              </div>
                              <p className="text-slate-600">{req.evidence_text}</p>
                            </div>
                            <div className="shrink-0">{getReqStatusBadge(req.status)}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Traceable Evidence Items */}
                    {rec.evidence && rec.evidence.length > 0 && (
                      <div>
                        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                          Traceable Supporting Evidence ({rec.evidence.length}):
                        </h4>
                        <div className="space-y-1.5">
                          {rec.evidence.map((ev, i) => (
                            <div
                              key={i}
                              className="p-2.5 rounded-lg bg-emerald-50/70 border border-emerald-200 text-xs text-emerald-900 flex items-start space-x-2"
                            >
                              <CheckCircle className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                              <div>
                                <span className="font-medium">{ev.evidence}</span>
                                <span className="text-[10px] text-emerald-700 ml-2">(Source: {ev.source})</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Missing Information Fields */}
                    {rec.missing_information && rec.missing_information.length > 0 && (
                      <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-900">
                        <span className="font-bold">Missing information required before confirmation:</span>
                        <ul className="list-disc list-inside mt-1 space-y-0.5">
                          {rec.missing_information.map((m, i) => (
                            <li key={i}>{m.replace(/_/g, ' ')}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
