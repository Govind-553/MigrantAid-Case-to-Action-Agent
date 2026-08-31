import React, { useState } from 'react';
import {
  ClipboardList,
  AlertOctagon,
  AlertTriangle,
  Pencil,
  Save,
  X,
  Plus,
  Trash2,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { CaseFact, CaseProfile, FactStatus } from '@/types';
import { mapFactStatus } from '@/lib/status';
import { cn } from '@/lib/cn';

/**
 * Normalizes and deduplicates a list of missing-information labels for display.
 *
 * WHY: The intake agent (LLM) can produce overlapping labels such as:
 *   "housing status or rent information", "exact housing status", "rent details"
 * These represent the same underlying gap and clutter the UI.
 *
 * HOW: Labels are tokenized and significant tokens (non-stop-words) are
 * compared.  Items sharing ≥60% of significant tokens are grouped; the
 * shortest label in the group is kept as the representative.
 *
 * IMPORTANT: This is purely a display-layer transformation.
 * The underlying verification engine evaluates each requirement independently —
 * this function only changes what the caseworker sees in the high-level summary.
 */
const STOP_WORDS = new Set([
  'or', 'and', 'the', 'a', 'an', 'of', 'for', 'to', 'in', 'on',
  'at', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
  'exact', 'current', 'specific', 'information', 'details', 'detail',
  'status', 'any',
]);

function tokenize(label: string): Set<string> {
  return new Set(
    label
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter((t) => t.length > 1 && !STOP_WORDS.has(t))
  );
}

function jaccard(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 && b.size === 0) return 1;
  let intersection = 0;
  Array.from(a).forEach((t) => {
    if (b.has(t)) intersection++;
  });
  const union = a.size + b.size - intersection;
  return union === 0 ? 0 : intersection / union;
}

export function normalizeMissingInfo(items: string[]): string[] {
  if (items.length === 0) return [];

  const tokenized = items.map((item) => ({ label: item, tokens: tokenize(item) }));
  const grouped: boolean[] = new Array(items.length).fill(false);
  const representatives: string[] = [];

  for (let i = 0; i < tokenized.length; i++) {
    if (grouped[i]) continue;
    const cluster = [i];
    for (let j = i + 1; j < tokenized.length; j++) {
      if (grouped[j]) continue;
      // If tokens are highly similar OR one label is a substring of the other
      const sim = jaccard(tokenized[i].tokens, tokenized[j].tokens);
      const aInB = tokenized[i].label.toLowerCase().includes(
        tokenized[j].label.toLowerCase().replace(/[^a-z\s]/g, '').trim()
      );
      const bInA = tokenized[j].label.toLowerCase().includes(
        tokenized[i].label.toLowerCase().replace(/[^a-z\s]/g, '').trim()
      );
      if (sim >= 0.6 || aInB || bInA) {
        cluster.push(j);
        grouped[j] = true;
      }
    }
    grouped[i] = true;
    // Keep shortest label as the representative for cleaner display
    const rep = cluster
      .map((k) => tokenized[k].label)
      .sort((a, b) => a.length - b.length)[0];
    representatives.push(rep);
  }

  return representatives;
}


interface FactsViewProps {
  profile: CaseProfile;
  onUpdateFacts: (facts: CaseFact[]) => Promise<void>;
  isLoading: boolean;
}

export const FactsView: React.FC<FactsViewProps> = ({
  profile,
  onUpdateFacts,
  isLoading,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [facts, setFacts] = useState<CaseFact[]>(profile.facts);

  const handleFactChange = (index: number, key: keyof CaseFact, value: any) => {
    const updated = [...facts];
    updated[index] = { ...updated[index], [key]: value };
    setFacts(updated);
  };

  const handleAddFact = () => {
    setFacts([
      ...facts,
      {
        field: 'new_field',
        value: 'value',
        status: 'explicit',
        source: 'caseworker_manual_entry',
      },
    ]);
  };

  const handleRemoveFact = (index: number) => {
    setFacts(facts.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    await onUpdateFacts(facts);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setFacts(profile.facts);
    setIsEditing(false);
  };

  const startEdit = () => {
    setFacts(profile.facts);
    setIsEditing(true);
  };

  return (
    <Card>
      <SectionHeader
        icon={<ClipboardList className="h-5 w-5" />}
        iconTone="brand"
        title="Extracted Structured Facts"
        description="Facts extracted from the case narrative. Review and correct before continuing — MigrantAid uses these values downstream."
        after={
          isEditing ? (
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={handleCancel}
                disabled={isLoading}
              >
                <X className="h-3.5 w-3.5" aria-hidden="true" />
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleSave}
                loading={isLoading}
                loadingLabel="Re-verifying…"
              >
                <Save className="h-3.5 w-3.5" aria-hidden="true" />
                Save &amp; Re-verify
              </Button>
            </div>
          ) : (
            <Button variant="secondary" size="sm" onClick={startEdit}>
              <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
              Edit facts
            </Button>
          )
        }
      />

      {/* Contradictions alert */}
      {profile.contradictions && profile.contradictions.length > 0 && (
        <div className="mb-4 p-4 bg-danger.bg border border-danger.border rounded-lg">
          <div className="flex items-start gap-3">
            <AlertOctagon className="h-5 w-5 text-danger shrink-0 mt-0.5" aria-hidden="true" />
            <div className="min-w-0">
              <h4 className="text-xs font-bold text-danger.text uppercase tracking-wider">
                Contradiction detected ({profile.contradictions.length})
              </h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
                Conflicting statements. Human clarification is required before proceeding.
              </p>
              <ul className="mt-2 space-y-1">
                {profile.contradictions.map((c, i) => (
                  <li key={i} className="text-xs text-danger.text dark:text-red-300 flex items-start gap-1.5">
                    <span aria-hidden="true">•</span>
                    <span>
                      <strong>{c.description}</strong>{' '}
                      <span className="text-slate-500 dark:text-slate-400">
                        ({c.fact_a.replace(/_/g, ' ')} vs {c.fact_b.replace(/_/g, ' ')})
                      </span>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Missing information alert */}
      {profile.missing_information && profile.missing_information.length > 0 && (() => {
        const normalized = normalizeMissingInfo(profile.missing_information);
        const collapsed = normalized.length < profile.missing_information.length;
        return (
          <div className="mb-4 p-4 bg-warning.bg border border-warning.border rounded-lg">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-4 w-4 text-warning shrink-0 mt-0.5" aria-hidden="true" />
              <div className="min-w-0 w-full">
                <div className="flex flex-wrap items-center justify-between gap-1 mb-1.5">
                  <span className="text-xs font-semibold text-warning.text">
                    Information needed ({profile.missing_information.length} field
                    {profile.missing_information.length !== 1 ? 's' : ''})
                  </span>
                  {collapsed && (
                    <span className="text-[10px] text-warning.text opacity-70">
                      {profile.missing_information.length - normalized.length} overlapping label
                      {profile.missing_information.length - normalized.length !== 1 ? 's' : ''} grouped
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {normalized.map((m, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-white dark:bg-slate-900 text-warning.text dark:text-amber-300 border border-warning.border dark:border-amber-800"
                    >
                      {m.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );
      })()}


      {/* Facts */}
      {!isEditing ? (
        profile.facts.length === 0 ? (
          <EmptyState
            icon={<ClipboardList className="h-6 w-6" />}
            title="No facts extracted yet"
            description="Analyze a case to see the structured facts extracted from the narrative."
          />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {profile.facts.map((fact, idx) => {
              const status = mapFactStatus(fact.status);
              return (
                <div
                  key={idx}
                  className={cn(
                    'p-3 rounded-lg border transition-colors',
                    fact.status === 'unknown'
                      ? 'border-warning.border dark:border-amber-800 bg-warning.bg/40 dark:bg-amber-950/30'
                      : fact.status === 'conflicting'
                      ? 'border-danger.border dark:border-red-800 bg-danger.bg/40 dark:bg-red-950/30'
                      : 'border-slate-100 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-800/60'
                  )}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider truncate">
                      {fact.field.replace(/_/g, ' ')}
                    </span>
                    <StatusBadge tone={status.tone} icon={status.icon} title={status.title} className="shrink-0">
                      {status.label}
                    </StatusBadge>
                  </div>
                  <div
                    className={cn(
                      'text-sm font-medium break-words',
                      fact.status === 'unknown'
                        ? 'text-warning.text dark:text-amber-300'
                        : fact.status === 'conflicting'
                        ? 'text-danger.text dark:text-red-300'
                        : 'text-slate-900 dark:text-slate-100'
                    )}
                  >
                    {typeof fact.value === 'boolean'
                      ? fact.value
                        ? 'Yes'
                        : 'No'
                      : String(fact.value ?? 'None')}
                  </div>
                  {fact.source && (
                    <div className="mt-2 text-[10px] text-slate-400 dark:text-slate-500 truncate">
                      Source: {fact.source.replace(/_/g, ' ')}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )
      ) : (
        <div className="space-y-2">
          {facts.map((f, idx) => (
            <div
              key={idx}
              className="flex flex-col sm:flex-row sm:items-center gap-2 bg-slate-50 dark:bg-slate-800/60 p-3 rounded-lg border border-slate-200 dark:border-slate-700"
            >
              <div className="flex flex-1 flex-col sm:flex-row gap-2">
                <input
                  type="text"
                  value={f.field}
                  onChange={(e) => handleFactChange(idx, 'field', e.target.value)}
                  placeholder="Field name"
                  aria-label="Fact field name"
                  className="flex-1 px-2.5 py-1.5 text-xs border border-slate-300 dark:border-slate-600 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                />
                <input
                  type="text"
                  value={typeof f.value === 'boolean' ? String(f.value) : f.value ?? ''}
                  onChange={(e) => {
                    let v: any = e.target.value;
                    if (v.toLowerCase() === 'true') v = true;
                    else if (v.toLowerCase() === 'false') v = false;
                    handleFactChange(idx, 'value', v);
                  }}
                  placeholder="Value"
                  aria-label="Fact value"
                  className="flex-1 px-2.5 py-1.5 text-xs border border-slate-300 dark:border-slate-600 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                />
                <select
                  value={f.status}
                  onChange={(e) => handleFactChange(idx, 'status', e.target.value as FactStatus)}
                  aria-label="Fact status"
                  className="flex-1 sm:flex-none px-2.5 py-1.5 text-xs border border-slate-300 dark:border-slate-600 rounded bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                >
                  <option value="explicit">Explicit</option>
                  <option value="inferred">Inferred</option>
                  <option value="conflicting">Conflicting</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
              <button
                type="button"
                onClick={() => handleRemoveFact(idx)}
                aria-label={`Remove fact ${f.field || 'untitled'}`}
                className="inline-flex h-8 w-8 items-center justify-center rounded-md text-slate-400 dark:text-slate-500 hover:text-danger dark:hover:text-red-400 hover:bg-danger.bg dark:hover:bg-red-950/40 shrink-0"
              >
                <Trash2 className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          ))}
          <Button variant="ghost" size="sm" onClick={handleAddFact}>
            <Plus className="h-3.5 w-3.5" aria-hidden="true" />
            Add fact
          </Button>
        </div>
      )}
    </Card>
  );
};
