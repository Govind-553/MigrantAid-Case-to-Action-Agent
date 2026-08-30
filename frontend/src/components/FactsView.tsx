import React, { useState } from 'react';
import { CheckCircle2, HelpCircle, AlertTriangle, Edit3, Save, X, Plus, AlertOctagon } from 'lucide-react';
import { CaseFact, CaseProfile, FactStatus } from '../types';

interface FactsViewProps {
  profile: CaseProfile;
  onUpdateFacts: (facts: CaseFact[]) => Promise<void>;
  isLoading: boolean;
}

export const FactsView: React.FC<FactsViewProps> = ({ profile, onUpdateFacts, isLoading }) => {
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

  const getStatusBadge = (status: FactStatus) => {
    switch (status) {
      case 'explicit':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="h-3 w-3" />
            <span>Explicit</span>
          </span>
        );
      case 'inferred':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
            <HelpCircle className="h-3 w-3" />
            <span>Inferred</span>
          </span>
        );
      case 'conflicting':
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium bg-rose-100 text-rose-800 border border-rose-200">
            <AlertOctagon className="h-3 w-3" />
            <span>Conflicting</span>
          </span>
        );
      case 'unknown':
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
            <AlertTriangle className="h-3 w-3" />
            <span>Unknown</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Extracted Structured Facts</h3>
          <p className="text-xs text-slate-500">
            Explicitly stated vs inferred facts from narrative intake. Frontline caseworker can edit and re-evaluate.
          </p>
        </div>
        <div>
          {isEditing ? (
            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={handleCancel}
                className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                <X className="h-3.5 w-3.5" />
                <span>Cancel</span>
              </button>
              <button
                type="button"
                onClick={handleSave}
                disabled={isLoading}
                className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium shadow-sm"
              >
                <Save className="h-3.5 w-3.5" />
                <span>Save & Re-verify</span>
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => {
                setFacts(profile.facts);
                setIsEditing(true);
              }}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-xs font-medium text-slate-700 transition-colors"
            >
              <Edit3 className="h-3.5 w-3.5 text-slate-500" />
              <span>Edit / Correct Facts</span>
            </button>
          )}
        </div>
      </div>

      {/* Contradictions Alert */}
      {profile.contradictions && profile.contradictions.length > 0 && (
        <div className="mb-4 p-3.5 bg-rose-50 border border-rose-200 rounded-lg">
          <div className="flex items-start space-x-2.5">
            <AlertOctagon className="h-5 w-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold text-rose-900 uppercase tracking-wider">
                Narrative Contradiction Detected ({profile.contradictions.length})
              </h4>
              {profile.contradictions.map((c, i) => (
                <p key={i} className="text-xs text-rose-700 mt-1">
                  • <strong>{c.description}</strong> ({c.fact_a} vs {c.fact_b})
                </p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Missing Information Alert */}
      {profile.missing_information && profile.missing_information.length > 0 && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <span className="text-xs font-semibold text-amber-900">
                Critical Missing Information:
              </span>
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {profile.missing_information.map((m, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-100 text-amber-800 border border-amber-300"
                  >
                    {m.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Facts Table / Form */}
      {isEditing ? (
        <div className="space-y-3">
          {facts.map((f, idx) => (
            <div key={idx} className="flex items-center space-x-2 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <input
                type="text"
                value={f.field}
                onChange={(e) => handleFactChange(idx, 'field', e.target.value)}
                placeholder="Field name"
                className="w-1/3 px-2 py-1 text-xs border border-slate-300 rounded bg-white"
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
                className="w-1/3 px-2 py-1 text-xs border border-slate-300 rounded bg-white"
              />
              <select
                value={f.status}
                onChange={(e) => handleFactChange(idx, 'status', e.target.value as FactStatus)}
                className="w-1/4 px-2 py-1 text-xs border border-slate-300 rounded bg-white"
              >
                <option value="explicit">Explicit</option>
                <option value="inferred">Inferred</option>
                <option value="conflicting">Conflicting</option>
                <option value="unknown">Unknown</option>
              </select>
              <button
                type="button"
                onClick={() => handleRemoveFact(idx)}
                className="text-slate-400 hover:text-rose-600 p-1"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddFact}
            className="inline-flex items-center space-x-1 text-xs text-emerald-700 hover:text-emerald-800 font-medium py-1"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>Add Additional Fact</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {profile.facts.map((fact, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-lg border border-slate-100 bg-slate-50/70 hover:bg-slate-100/70 transition-colors"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  {fact.field.replace(/_/g, ' ')}
                </span>
                {getStatusBadge(fact.status)}
              </div>
              <div className="text-sm font-medium text-slate-900 truncate">
                {typeof fact.value === 'boolean'
                  ? fact.value ? 'Yes (True)' : 'No (False)'
                  : String(fact.value ?? 'None')}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
