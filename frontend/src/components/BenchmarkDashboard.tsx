import React, { useEffect, useState } from 'react';
import {
  Award,
  TrendingUp,
  ShieldCheck,
  FileSearch,
  HelpCircle,
  Clock,
  BarChart3,
  RefreshCw,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { ComparisonReport } from '@/types';
import { getEvaluationComparison } from '@/lib/api';

export const BenchmarkDashboard: React.FC = () => {
  const [data, setData] = useState<ComparisonReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchComparison = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getEvaluationComparison();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Unable to load the benchmark evaluation right now.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchComparison();
  }, []);

  if (isLoading) {
    return (
      <LoadingState
        title="Loading benchmark results"
        description={`Comparing baseline vs. MigrantAid across the evaluation cases…`}
      />
    );
  }

  if (error || !data) {
    return (
      <ErrorState
        message={error || 'Unable to load benchmark data.'}
        details="The evaluation comparison endpoint could not be reached. Please confirm the backend is running, then retry."
        onRetry={fetchComparison}
      />
    );
  }

  const { baseline_summary: b, agentic_summary: a, improvements: imp } = data;

  const dimensions = [
    { key: 'primary_need', label: 'Primary Need Identification', max: 20 },
    { key: 'resource', label: 'Resource Identification', max: 20 },
    { key: 'evidence', label: 'Evidence Traceability', max: 20 },
    { key: 'missing_information', label: 'Missing Info Detection', max: 15 },
    { key: 'unsupported_claim', label: 'No Unsupported Claims', max: 15 },
    { key: 'actionable_next_step', label: 'Actionable Next Step', max: 10 },
  ];

  const kpis = [
    {
      label: 'VARR Success Rate',
      value: `${a.varr_percentage}%`,
      delta: `+${imp.varr_delta_percentage.toFixed(1)}%`,
      note: `Baseline ${b.varr_percentage}% (${b.successful_cases}/${data.total_cases}) → ${a.varr_percentage}% (${a.successful_cases}/${data.total_cases})`,
      icon: <Award className="h-5 w-5" />,
      tone: 'text-brand-600 bg-brand-50',
    },
    {
      label: 'Average Total Score',
      value: `${a.avg_total_score} / 100`,
      delta: `+${imp.score_delta.toFixed(1)} pts`,
      note: `Baseline ${b.avg_total_score} → MigrantAid ${a.avg_total_score}`,
      icon: <TrendingUp className="h-5 w-5" />,
      tone: 'text-blue-600 bg-blue-50',
    },
    {
      label: 'Evidence Traceability',
      value: `${(a.avg_dimension_scores['evidence'] ?? 0).toFixed(1)} / 20`,
      delta: `+${((a.avg_dimension_scores['evidence'] ?? 0) - (b.avg_dimension_scores['evidence'] ?? 0)).toFixed(1)} pts`,
      note: 'Fact-to-requirement grounding preserved',
      icon: <FileSearch className="h-5 w-5" />,
      tone: 'text-emerald-600 bg-emerald-50',
    },
    {
      label: 'Unsupported Claims',
      value: `${b.failure_category_distribution['UNSUPPORTED_CLAIM'] ?? 0} → ${a.failure_category_distribution['UNSUPPORTED_CLAIM'] ?? 0}`,
      delta: `-${((b.failure_category_distribution['UNSUPPORTED_CLAIM'] ?? 0) - (a.failure_category_distribution['UNSUPPORTED_CLAIM'] ?? 0)) * 100 / Math.max(1, b.failure_category_distribution['UNSUPPORTED_CLAIM'] ?? 1)}%`,
      note: 'False eligibility claims eliminated',
      icon: <ShieldCheck className="h-5 w-5" />,
      tone: 'text-red-600 bg-red-50',
    },
    {
      label: 'Latency / Case',
      value: `${a.avg_latency_ms.toFixed(0)} ms`,
      delta: b.avg_latency_ms > 0 ? `${((a.avg_latency_ms - b.avg_latency_ms) / b.avg_latency_ms * 100).toFixed(0)}%` : '—',
      note: `Baseline ${b.avg_latency_ms.toFixed(0)} ms → MigrantAid ${a.avg_latency_ms.toFixed(0)} ms`,
      icon: <Clock className="h-5 w-5" />,
      tone: 'text-amber-600 bg-amber-50',
    },
    {
      label: 'Missing Info Detected',
      value: `${(a.avg_dimension_scores['missing_information'] ?? 0).toFixed(1)} / 15`,
      delta: `+${((a.avg_dimension_scores['missing_information'] ?? 0) - (b.avg_dimension_scores['missing_information'] ?? 0)).toFixed(1)} pts`,
      note: 'Unknown eligibility surfaced, not glossed over',
      icon: <HelpCircle className="h-5 w-5" />,
      tone: 'text-violet-600 bg-violet-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">Evaluation &amp; Benchmark</h2>
        <p className="text-sm text-slate-500 mt-1">
          Side-by-side comparison of the single-prompt baseline vs. MigrantAid across{' '}
          {data.total_cases} fixed evaluation cases.
        </p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {kpis.map((k) => (
          <Card key={k.label} className="relative overflow-hidden">
            <div className="flex items-start justify-between gap-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {k.label}
              </span>
              <span className={`p-1.5 rounded-lg ${k.tone}`} aria-hidden="true">
                {k.icon}
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-3">
              <span className="text-2xl font-extrabold text-slate-900 tabular-nums">
                {k.value}
              </span>
              <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 whitespace-nowrap">
                {k.delta}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-2">{k.note}</p>
          </Card>
        ))}
      </div>

      {/* Dimension comparison */}
      <Card>
        <div className="flex items-center gap-3 mb-4 pb-3 border-b border-slate-100">
          <div className="p-2 bg-slate-100 text-slate-700 rounded-lg" aria-hidden="true">
            <BarChart3 className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-900">
              Scoring Dimensions
            </h3>
            <p className="text-xs text-slate-500">
              Average scores out of the maximum for each dimension
            </p>
          </div>
        </div>

        <div className="hidden sm:block overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 w-1/3">Dimension</th>
                <th className="py-3 px-4 w-1/4">Baseline</th>
                <th className="py-3 px-4 w-1/4">MigrantAid</th>
                <th className="py-3 px-4 text-right w-1/6">Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {dimensions.map((dim) => {
                const bVal = b.avg_dimension_scores[dim.key] || 0;
                const aVal = a.avg_dimension_scores[dim.key] || 0;
                const delta = aVal - bVal;
                return (
                  <tr key={dim.key} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-medium text-slate-900">{dim.label}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-24 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-slate-400 rounded-full"
                            style={{ width: `${(bVal / dim.max) * 100}%` }}
                          />
                        </div>
                        <span className="font-mono text-slate-600 tabular-nums">{bVal.toFixed(1)}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-24 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-brand-600 rounded-full"
                            style={{ width: `${(aVal / dim.max) * 100}%` }}
                          />
                        </div>
                        <span className="font-mono font-bold text-slate-900 tabular-nums">{aVal.toFixed(1)}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded text-xs font-semibold tabular-nums ${
                          delta > 0
                            ? 'bg-emerald-100 text-emerald-800'
                            : delta === 0
                            ? 'bg-slate-100 text-slate-700'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1)} pts
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Mobile card view */}
        <div className="sm:hidden space-y-3">
          {dimensions.map((dim) => {
            const bVal = b.avg_dimension_scores[dim.key] || 0;
            const aVal = a.avg_dimension_scores[dim.key] || 0;
            const delta = aVal - bVal;
            return (
              <div key={dim.key} className="p-3 rounded-lg border border-slate-200 bg-white">
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-xs font-medium text-slate-900">{dim.label}</span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[11px] font-semibold ${
                      delta > 0 ? 'bg-emerald-100 text-emerald-800' : delta === 0 ? 'bg-slate-100 text-slate-700' : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1)} pts
                  </span>
                </div>
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>Baseline</span>
                    <span className="font-mono">{bVal.toFixed(1)} / {dim.max}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>MigrantAid</span>
                    <span className="font-mono font-bold text-slate-900">{aVal.toFixed(1)} / {dim.max}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Failure mode reductions */}
      <Card>
        <h3 className="text-base font-semibold text-slate-900 mb-1">
          Failure Mode Reductions
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          How deterministic verification resolved single-prompt LLM vulnerabilities.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {[
            { code: 'EVIDENCE_MISS', desc: 'Ungrounded assertions without fact-to-requirement links', b: b, a: a },
            { code: 'UNSUPPORTED_CLAIM', desc: 'Claiming eligibility despite missing data', b: b, a: a },
            { code: 'CONTRADICTION_MISS', desc: 'Overlooking conflicting case statements', b: b, a: a },
          ].map((f) => {
            const bCount = b.failure_category_distribution[f.code] || 0;
            const aCount = a.failure_category_distribution[f.code] || 0;
            return (
              <div key={f.code} className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                <span className="text-xs font-bold text-slate-900 block mb-1 font-mono">
                  {f.code}
                </span>
                <p className="text-xs text-slate-600 mb-2">{f.desc}</p>
                <div className="flex items-center justify-between text-xs font-bold tabular-nums">
                  <span className="text-red-600">Baseline: {bCount}</span>
                  <span className="text-slate-400" aria-hidden="true">→</span>
                  <span className="text-emerald-600">MigrantAid: {aCount}</span>
                </div>
              </div>
            );
          })}
        </div>

        <p className="mt-4 text-[11px] text-slate-400">
          Results reflect the fixed evaluation dataset (v{data.dataset_version}). Reported
          metrics come directly from the evaluation runner — no values are simulated.
        </p>
      </Card>
    </div>
  );
};
