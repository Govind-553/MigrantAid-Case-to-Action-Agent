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
              <p className="text-xs text-slate-600 mt-0.5">
                Conflicting statements. Human clarification is required before proceeding.
              </p>
              <ul className="mt-2 space-y-1">
                {profile.contradictions.map((c, i) => (
                  <li key={i} className="text-xs text-danger.text flex items-start gap-1.5">
                    <span aria-hidden="true">•</span>
                    <span>
                      <strong>{c.description}</strong>{' '}
                      <span className="text-slate-500">
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
      {profile.missing_information && profile.missing_information.length > 0 && (
        <div className="mb-4 p-4 bg-warning.bg border border-warning.border rounded-lg">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-4 w-4 text-warning shrink-0 mt-0.5" aria-hidden="true" />
            <div className="min-w-0">
              <span className="text-xs font-semibold text-warning.text">
                Critical missing information
              </span>
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {profile.missing_information.map((m, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-white text-warning.text border border-warning.border"
                  >
                    {m.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

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
                      ? 'border-warning.border bg-warning.bg/40'
                      : fact.status === 'conflicting'
                      ? 'border-danger.border bg-danger.bg/40'
                      : 'border-slate-100 bg-slate-50/60'
                  )}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider truncate">
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
                        ? 'text-warning.text'
                        : fact.status === 'conflicting'
                        ? 'text-danger.text'
                        : 'text-slate-900'
                    )}
                  >
                    {typeof fact.value === 'boolean'
                      ? fact.value
                        ? 'Yes'
                        : 'No'
                      : String(fact.value ?? 'None')}
                  </div>
                  {fact.source && (
                    <div className="mt-2 text-[10px] text-slate-400 truncate">
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
              className="flex flex-col sm:flex-row sm:items-center gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200"
            >
              <div className="flex flex-1 flex-col sm:flex-row gap-2">
                <input
                  type="text"
                  value={f.field}
                  onChange={(e) => handleFactChange(idx, 'field', e.target.value)}
                  placeholder="Field name"
                  aria-label="Fact field name"
                  className="flex-1 px-2.5 py-1.5 text-xs border border-slate-300 rounded bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
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
                  className="flex-1 px-2.5 py-1.5 text-xs border border-slate-300 rounded bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                />
                <select
                  value={f.status}
                  onChange={(e) => handleFactChange(idx, 'status', e.target.value as FactStatus)}
                  aria-label="Fact status"
                  className="flex-1 sm:flex-none px-2.5 py-1.5 text-xs border border-slate-300 rounded bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
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
                className="inline-flex h-8 w-8 items-center justify-center rounded-md text-slate-400 hover:text-danger hover:bg-danger.bg shrink-0"
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
