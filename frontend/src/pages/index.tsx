import React, { useState, useCallback, useMemo } from 'react';
import Head from 'next/head';
import { FileText, ShieldCheck, ArrowRight } from 'lucide-react';
import { Header } from '@/components/Header';
import { IntakeView } from '@/components/IntakeView';
import { FactsView } from '@/components/FactsView';
import { NeedsView } from '@/components/NeedsView';
import { RecommendationsView } from '@/components/RecommendationsView';
import { ActionPlanView } from '@/components/ActionPlanView';
import { HumanReviewView } from '@/components/HumanReviewView';
import { TrajectoryView } from '@/components/TrajectoryView';
import { BenchmarkDashboard } from '@/components/BenchmarkDashboard';
import { WorkflowNav } from '@/components/ui/WorkflowNav';
import { CaseStatusBar } from '@/components/ui/CaseStatusBar';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { ErrorState } from '@/components/ui/ErrorState';
import { CaseFact, CaseState, HumanReview } from '@/types';
import { createCase, updateCaseFacts, submitHumanReview } from '@/lib/api';
import {
  getAvailableStages,
  getInitialStage,
  WORKFLOW_STAGES,
  type WorkflowStageId,
} from '@/lib/workflow';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'casework' | 'benchmark'>('casework');
  const [currentCase, setCurrentCase] = useState<CaseState | null>(null);
  const [activeStage, setActiveStage] = useState<WorkflowStageId>('intake');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const available = useMemo(
    () => getAvailableStages(currentCase),
    [currentCase]
  );

  const handleCreateCase = useCallback(
    async (narrative: string, caseId?: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const state = await createCase(narrative, caseId);
        setCurrentCase(state);
        setActiveStage(getInitialStage(state));
        setActiveTab('casework');
      } catch (err: any) {
        setError(err.message || 'Unable to analyze this case right now.');
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const handleUpdateFacts = useCallback(
    async (facts: CaseFact[]) => {
      if (!currentCase) return;
      setIsLoading(true);
      setError(null);
      try {
        const updated = await updateCaseFacts(currentCase.case_id, facts);
        setCurrentCase(updated);
      } catch (err: any) {
        setError(err.message || 'Unable to update facts and re-verify right now.');
      } finally {
        setIsLoading(false);
      }
    },
    [currentCase]
  );

  const handleSubmitReview = useCallback(
    async (decision: HumanReview['decision'], notes?: string) => {
      if (!currentCase) return;
      setIsLoading(true);
      setError(null);
      try {
        const updated = await submitHumanReview(currentCase.case_id, decision, notes);
        setCurrentCase(updated);
      } catch (err: any) {
        setError(err.message || 'Unable to record your decision right now.');
      } finally {
        setIsLoading(false);
      }
    },
    [currentCase]
  );

  const goToNextStage = useCallback(() => {
    if (!currentCase) return;
    const order: WorkflowStageId[] = WORKFLOW_STAGES.map((s) => s.id);
    const idx = order.indexOf(activeStage);
    for (let i = idx + 1; i < order.length; i++) {
      if (available.has(order[i])) {
        setActiveStage(order[i]);
        return;
      }
    }
  }, [activeStage, available, currentCase]);

  const renderStage = () => {
    if (!currentCase) return null;

    switch (activeStage) {
      case 'facts':
        return currentCase.profile ? (
          <FactsView
            profile={currentCase.profile}
            onUpdateFacts={handleUpdateFacts}
            isLoading={isLoading}
          />
        ) : null;
      case 'needs':
        return currentCase.needs_assessment ? (
          <NeedsView assessment={currentCase.needs_assessment} />
        ) : null;
      case 'resources':
      case 'verification':
        return <RecommendationsView recommendations={currentCase.verified_recommendations} />;
      case 'action-plan':
        return currentCase.action_plan ? (
          <ActionPlanView actionPlan={currentCase.action_plan} />
        ) : null;
      case 'review':
        return (
          <HumanReviewView
            review={currentCase.human_review}
            onSubmitReview={handleSubmitReview}
            isLoading={isLoading}
          />
        );
      case 'trajectory':
        return currentCase.trajectory && currentCase.trajectory.length > 0 ? (
          <TrajectoryView trajectory={currentCase.trajectory} />
        ) : null;
      case 'intake':
      default:
        return <IntakeView onSubmit={handleCreateCase} isLoading={isLoading} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Head>
        <title>MigrantAid — Case-to-Action Assistant</title>
        <meta
          name="description"
          content="MigrantAid — turn messy community cases into evidence-backed, human-reviewed action plans."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      <Header currentTab={activeTab} onTabChange={setActiveTab} />

      <main
        id="main-content"
        className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8"
      >
        {error && (
          <div className="mb-6" role="alert">
            <ErrorState
              message={error}
              onRetry={() => setError(null)}
              retryLabel="Dismiss"
            />
          </div>
        )}

        {activeTab === 'benchmark' ? (
          <BenchmarkDashboard />
        ) : (
          <div className="space-y-6">
            {/* Hero — shown on first screen before a case exists */}
            {!currentCase && (
              <div className="text-center max-w-2xl mx-auto px-2">
                <span className="inline-flex items-center gap-2 text-xs font-semibold text-brand-700 bg-brand-50 border border-brand-200 rounded-full px-3 py-1">
                  <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
                  AI assists. Human decides.
                </span>
                <h1 className="mt-4 text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">
                  Turn messy community cases into evidence-backed, human-reviewed action plans.
                </h1>
                <p className="mt-3 text-slate-500 text-sm sm:text-base">
                  MigrantAid helps frontline workers turn an incomplete description into
                  structured facts, prioritized needs, verified resource matches, and a clear
                  action plan — with the human always in control.
                </p>
              </div>
            )}

            {/* Case not yet created: full-width intake */}
            {!currentCase && (
              <IntakeView onSubmit={handleCreateCase} isLoading={isLoading} />
            )}

            {/* Active case: workflow layout */}
            {currentCase && (
              <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-6">
                {/* Workflow navigation sidebar / mobile strip */}
                <aside className="lg:pb-0">
                  <div className="lg:sticky lg:top-20">
                    <p className="hidden lg:block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
                      Case workflow
                    </p>
                    <WorkflowNav
                      activeStage={activeStage}
                      available={available}
                      onSelect={setActiveStage}
                    />
                  </div>
                </aside>

                {/* Stage content */}
                <div className="min-w-0 space-y-5">
                  <CaseStatusBar caseState={currentCase} />

                  <div key={activeStage} className="animate-fade-in">
                    {renderStage() ?? (
                      <Card>
                        <p className="text-sm text-slate-500 text-center py-8">
                          This part of the case has not been generated yet. Use{' '}
                          <strong>Continue to next step</strong> or select another stage.
                        </p>
                      </Card>
                    )}
                  </div>

                  {/* Continue affordance */}
                  <div className="flex justify-end">
                    {activeStage !== 'trajectory' && activeStage !== 'intake' && (
                      <Button variant="secondary" size="md" onClick={goToNextStage}>
                        Continue to next step
                        <ArrowRight className="h-4 w-4" aria-hidden="true" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-slate-200 py-6 mt-12 text-center text-xs text-slate-500">
        <p>MigrantAid — Evidence-Backed Case-to-Action Casework Assistant</p>
        <p className="mt-1 text-[11px] text-slate-400">
          Strict Evidence Traceability · Human-in-the-Loop Governance · Deterministic Evaluation
          Rubric
        </p>
      </footer>
    </div>
  );
}
