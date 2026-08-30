import React, { useState } from 'react';
import { Send, FileText, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';

interface IntakeViewProps {
  onSubmit: (narrative: string, caseId?: string) => Promise<void>;
  isLoading: boolean;
}

const SAMPLE_CASES = [
  {
    id: 'CASE-001',
    title: 'CASE-001: Unemployed worker with dependents',
    category: 'Ordinary',
    text: 'A migrant worker in Pune recently lost his job. He has two children and says the household currently has no other income. He has an identity document and a bank account.',
  },
  {
    id: 'CASE-002',
    title: 'CASE-002: Housing support with missing income (Incomplete)',
    category: 'Incomplete Information',
    text: "A migrant family living in Pune is struggling to pay rent after the main earner's work hours were reduced. They want to know what housing support may be available.",
  },
  {
    id: 'CASE-003',
    title: 'CASE-003: Documentation help after relocation',
    category: 'Documentation',
    text: 'A worker recently moved to Pune for work and needs help understanding which identity and address documents are needed to access local services. He has one identity document but no proof of current address.',
  },
  {
    id: 'CASE-008',
    title: 'CASE-008: Contradictory employment statements',
    category: 'Contradiction',
    text: 'A worker first says he is unemployed, but later says he is currently working part-time three days a week. He asks about employment support.',
  },
  {
    id: 'CASE-005',
    title: 'CASE-005: Food & basic support with unknown spouse income',
    category: 'Basic Support',
    text: 'A worker says food expenses have become difficult after a recent job loss. He lives with his spouse and children, but does not know whether his spouse’s current income affects access to support.',
  },
  {
    id: 'CASE-006',
    title: 'CASE-006: Multi-need (Housing + Employment + Food)',
    category: 'Multi-Need',
    text: 'A migrant couple in Pune has recently lost one source of income and is behind on rent. They also want help finding new work. They have two school-age children.',
  },
];

export const IntakeView: React.FC<IntakeViewProps> = ({ onSubmit, isLoading }) => {
  const [narrative, setNarrative] = useState(SAMPLE_CASES[0].text);
  const [selectedCaseId, setSelectedCaseId] = useState(SAMPLE_CASES[0].id);

  const handleSelectSample = (sample: typeof SAMPLE_CASES[0]) => {
    setSelectedCaseId(sample.id);
    setNarrative(sample.text);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!narrative.trim() || isLoading) return;
    onSubmit(narrative, selectedCaseId || undefined);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Case Intake & Narrative</h2>
            <p className="text-xs text-slate-500">
              Input raw beneficiary story, interview notes, or select a standardized evaluation case
            </p>
          </div>
        </div>
      </div>

      {/* Preset Evaluation Case Selector */}
      <div className="mb-4">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
          Load Pre-Configured Evaluation Benchmark Case:
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {SAMPLE_CASES.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => handleSelectSample(s)}
              className={`text-left p-2.5 rounded-lg border text-xs transition-all ${
                selectedCaseId === s.id
                  ? 'border-emerald-500 bg-emerald-50/50 ring-1 ring-emerald-400 font-medium text-emerald-900'
                  : 'border-slate-200 bg-slate-50/50 hover:bg-slate-100 text-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-900">{s.id}</span>
                <span className="text-[10px] bg-slate-200/70 text-slate-600 px-1.5 py-0.5 rounded">
                  {s.category}
                </span>
              </div>
              <p className="truncate mt-1 text-slate-600">{s.title.split(': ')[1]}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Narrative Input Form */}
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="narrative" className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
            Beneficiary Case Narrative / Interview Notes:
          </label>
          <textarea
            id="narrative"
            rows={4}
            value={narrative}
            onChange={(e) => {
              setNarrative(e.target.value);
              setSelectedCaseId('');
            }}
            placeholder="Type or paste messy beneficiary situation description here..."
            className="w-full px-3.5 py-2.5 text-sm text-slate-800 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all placeholder:text-slate-400"
            required
          />
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <Sparkles className="h-4 w-4 text-emerald-600" />
            <span>Executes 6-stage pipeline: Intake → Needs → Matching → Verification → Action Planning → Quality Gate</span>
          </div>

          <button
            type="submit"
            disabled={isLoading || !narrative.trim()}
            className="inline-flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm px-5 py-2.5 rounded-lg shadow-sm hover:shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {isLoading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Running Agent Pipeline...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span>Process Case</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
