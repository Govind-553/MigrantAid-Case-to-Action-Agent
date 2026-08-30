import React, { useState } from 'react';
import { FileText, Sparkles, Info } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Field, inputClasses } from '@/components/ui/Field';
import { cn } from '@/lib/cn';

interface IntakeViewProps {
  onSubmit: (narrative: string, caseId?: string) => Promise<void>;
  isLoading: boolean;
}

const SAMPLE_CASES = [
  {
    id: 'CASE-001',
    title: 'Unemployed worker with dependents',
    category: 'Ordinary',
    text: 'A migrant worker in Pune recently lost his job. He has two children and says the household currently has no other income. He has an identity document and a bank account.',
  },
  {
    id: 'CASE-002',
    title: 'Housing support with missing income',
    category: 'Incomplete',
    text: "A migrant family living in Pune is struggling to pay rent after the main earner's work hours were reduced. They want to know what housing support may be available.",
  },
  {
    id: 'CASE-003',
    title: 'Documentation help after relocation',
    category: 'Documentation',
    text: 'A worker recently moved to Pune for work and needs help understanding which identity and address documents are needed to access local services. He has one identity document but no proof of current address.',
  },
  {
    id: 'CASE-008',
    title: 'Contradictory employment statements',
    category: 'Contradiction',
    text: 'A worker first says he is unemployed, but later says he is currently working part-time three days a week. He asks about employment support.',
  },
  {
    id: 'CASE-005',
    title: 'Food & basic support, unknown spouse income',
    category: 'Basic Support',
    text: 'A worker says food expenses have become difficult after a recent job loss. He lives with his spouse and children, but does not know whether his spouse’s current income affects access to support.',
  },
  {
    id: 'CASE-006',
    title: 'Multi-need: housing + employment + food',
    category: 'Multi-Need',
    text: 'A migrant couple in Pune has recently lost one source of income and is behind on rent. They also want help finding new work. They have two school-age children.',
  },
];

export const IntakeView: React.FC<IntakeViewProps> = ({ onSubmit, isLoading }) => {
  const [narrative, setNarrative] = useState(SAMPLE_CASES[0].text);
  const [selectedCaseId, setSelectedCaseId] = useState(SAMPLE_CASES[0].id);
  const [touched, setTouched] = useState(false);

  const hasContent = narrative.trim().length > 0;
  const showValidation = touched && !hasContent;

  const handleSelectSample = (sample: typeof SAMPLE_CASES[0]) => {
    setSelectedCaseId(sample.id);
    setNarrative(sample.text);
    setTouched(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!narrative.trim() || isLoading) return;
    onSubmit(narrative, selectedCaseId || undefined);
  };

  return (
    <Card>
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-slate-900 leading-snug">
          Describe the person&apos;s situation
        </h2>
        <p className="text-sm text-slate-500 mt-1">
          Write the case in your own words — it doesn&apos;t need to be structured.
          MigrantAid will turn it into an evidence-backed, human-reviewed action plan.
        </p>
      </div>

      {/* Pre-loaded evaluation cases */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-2">
          <Info className="h-3.5 w-3.5 text-slate-400" aria-hidden="true" />
          <span className="text-xs font-semibold text-slate-600">
            Load a pre-configured evaluation case to start quickly
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {SAMPLE_CASES.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => handleSelectSample(s)}
              aria-pressed={selectedCaseId === s.id}
              className={cn(
                'text-left p-2.5 rounded-lg border text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
                selectedCaseId === s.id
                  ? 'border-brand-300 bg-brand-50 ring-1 ring-brand-300 text-brand-900'
                  : 'border-slate-200 bg-slate-50/50 hover:bg-slate-100 text-slate-700'
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-[11px] font-bold text-slate-900">
                  {s.id}
                </span>
                <span className="text-[10px] bg-white text-slate-500 px-1.5 py-0.5 rounded border border-slate-200 whitespace-nowrap">
                  {s.category}
                </span>
              </div>
              <p className="mt-1 line-clamp-2 text-slate-600">{s.title}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Narrative form */}
      <form onSubmit={handleSubmit} noValidate>
        <Field
          label="Beneficiary case narrative"
          htmlFor="narrative"
          hint={`${narrative.length} characters`}
          required
          error={showValidation ? 'Please describe the person’s situation to analyze the case.' : undefined}
        >
          <textarea
            id="narrative"
            rows={5}
            value={narrative}
            onChange={(e) => {
              setNarrative(e.target.value);
              setSelectedCaseId('');
              setTouched(true);
            }}
            placeholder="e.g. A worker came to Pune from Bihar for work. He lost his job recently and has two children. He has Aadhaar and a bank account but is unsure what support is available."
            aria-required="true"
            aria-invalid={showValidation}
            className={cn(
              inputClasses,
              'min-h-[120px] resize-y leading-relaxed',
              showValidation && 'border-danger focus:border-danger focus:ring-danger/30'
            )}
          />
        </Field>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mt-4">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Sparkles className="h-4 w-4 text-brand-600" aria-hidden="true" />
            <span className="hidden sm:inline">
              6-stage pipeline: Intake → Needs → Matching → Verification → Action &rarr; Quality
            </span>
            <span className="sm:hidden">
              6-stage assisted analysis pipeline
            </span>
          </div>

          <Button
            type="submit"
            size="lg"
            loading={isLoading}
            loadingLabel={isLoading ? 'Analyzing case…' : undefined}
            disabled={!hasContent}
            className="sm:w-auto"
          >
            <FileText className="h-4 w-4" aria-hidden="true" />
            Analyze Case
          </Button>
        </div>
      </form>
    </Card>
  );
};
