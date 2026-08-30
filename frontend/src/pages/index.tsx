import React, { useState } from 'react';
import Head from 'next/head';
import { Header } from '@/components/Header';
import { IntakeView } from '@/components/IntakeView';
import { FactsView } from '@/components/FactsView';
import { NeedsView } from '@/components/NeedsView';
import { RecommendationsView } from '@/components/RecommendationsView';
import { ActionPlanView } from '@/components/ActionPlanView';
import { HumanReviewView } from '@/components/HumanReviewView';
import { TrajectoryView } from '@/components/TrajectoryView';
import { BenchmarkDashboard } from '@/components/BenchmarkDashboard';
import { CaseFact, CaseState, HumanReview } from '@/types';
import { createCase, updateCaseFacts, submitHumanReview } from '@/lib/api';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'casework' | 'benchmark'>('casework');
  const [currentCase, setCurrentCase] = useState<CaseState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateCase = async (narrative: string, caseId?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const state = await createCase(narrative, caseId);
      setCurrentCase(state);
    } catch (err: any) {
      setError(err.message || 'Failed to process case with agentic pipeline.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateFacts = async (facts: CaseFact[]) => {
    if (!currentCase) return;
    setIsLoading(true);
    setError(null);
    try {
      const updated = await updateCaseFacts(currentCase.case_id, facts);
      setCurrentCase(updated);
    } catch (err: any) {
      setError(err.message || 'Failed to update facts and re-verify.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitReview = async (decision: HumanReview['decision'], notes?: string) => {
    if (!currentCase) return;
    setIsLoading(true);
    setError(null);
    try {
      const updated = await submitHumanReview(currentCase.case_id, decision, notes);
      setCurrentCase(updated);
    } catch (err: any) {
      setError(err.message || 'Failed to submit caseworker review decision.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Head>
        <title>MigrantAid — Case-to-Action Assistant</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <Header currentTab={activeTab} onTabChange={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Error notification */}
        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center justify-between shadow-sm">
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="text-rose-600 hover:text-rose-900 font-bold ml-4"
            >
              ✕
            </button>
          </div>
        )}

        {activeTab === 'benchmark' ? (
          <BenchmarkDashboard />
        ) : (
          <div className="space-y-8">
            {/* Case Intake Section */}
            <IntakeView onSubmit={handleCreateCase} isLoading={isLoading} />

            {/* Active Case Pipeline Views */}
            {currentCase && (
              <div className="space-y-8 animate-fadeIn">
                {/* Status Bar */}
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-xs font-mono font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-md">
                      {currentCase.case_id}
                    </span>
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Workflow Status:
                    </span>
                    <span className="text-xs font-bold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2.5 py-0.5 rounded-full">
                      {currentCase.workflow_state}
                    </span>
                  </div>

                  <div className="text-xs text-slate-500 flex items-center space-x-4">
                    <span>
                      Needs Identified: <strong>{currentCase.needs_assessment?.needs.length || 0}</strong>
                    </span>
                    <span>•</span>
                    <span>
                      Verified Recommendations: <strong>{currentCase.verified_recommendations.length || 0}</strong>
                    </span>
                    <span>•</span>
                    <span>
                      Action Steps: <strong>{currentCase.action_plan?.actions.length || 0}</strong>
                    </span>
                  </div>
                </div>

                {/* Section 1: Facts Review */}
                {currentCase.profile && (
                  <FactsView
                    profile={currentCase.profile}
                    onUpdateFacts={handleUpdateFacts}
                    isLoading={isLoading}
                  />
                )}

                {/* Section 2: Needs Assessment */}
                {currentCase.needs_assessment && (
                  <NeedsView assessment={currentCase.needs_assessment} />
                )}

                {/* Section 3: Verified Recommendations & Traceable Evidence */}
                <RecommendationsView
                  recommendations={currentCase.verified_recommendations}
                />

                {/* Section 4: Action Plan */}
                {currentCase.action_plan && (
                  <ActionPlanView actionPlan={currentCase.action_plan} />
                )}

                {/* Section 5: Human Review Gate */}
                <HumanReviewView
                  review={currentCase.human_review}
                  onSubmitReview={handleSubmitReview}
                  isLoading={isLoading}
                />

                {/* Section 6: Trajectory & Observability */}
                {currentCase.trajectory && currentCase.trajectory.length > 0 && (
                  <TrajectoryView trajectory={currentCase.trajectory} />
                )}
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-slate-200 py-6 mt-12 text-center text-xs text-slate-500">
        <p>MigrantAid — Evidence-Backed Case-to-Action Casework Assistant</p>
        <p className="mt-1 text-[11px] text-slate-400">
          Strict Evidence Traceability • Human-in-the-Loop Governance • Deterministic Evaluation Rubric
        </p>
      </footer>
    </div>
  );
}
