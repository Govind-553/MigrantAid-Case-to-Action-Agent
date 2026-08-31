import React, { useState } from 'react';
import {
  Activity,
  Bot,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock,
  AlertTriangle,
  PlayCircle,
  User,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { EmptyState } from '@/components/ui/EmptyState';
import { AgentEvent } from '@/types';
import { cn } from '@/lib/cn';

interface TrajectoryViewProps {
  trajectory: AgentEvent[];
}

/**
 * Groups raw AgentEvents by (stage, agent) into logical workflow stages.
 *
 * Root cause of the "duplicate" appearance:
 *   The backend intentionally logs TWO events per stage — stage_start and
 *   stage_complete — for observability. Both are legitimate and auditable.
 *   This grouping surfaces them as a single stage card with expandable
 *   sub-events, preserving full auditability without visual confusion.
 */
interface StageGroup {
  key: string;
  stage: string;
  agent: string;
  events: AgentEvent[];
  hasError: boolean;
  totalLatencyMs: number;
}

function groupTrajectoryEvents(events: AgentEvent[]): StageGroup[] {
  const groups: StageGroup[] = [];
  const seen = new Map<string, StageGroup>();

  for (const event of events) {
    const key = `${event.stage}::${event.agent}`;
    if (!seen.has(key)) {
      const group: StageGroup = {
        key,
        stage: event.stage,
        agent: event.agent,
        events: [],
        hasError: false,
        totalLatencyMs: 0,
      };
      seen.set(key, group);
      groups.push(group);
    }
    const group = seen.get(key)!;
    group.events.push(event);
    if (event.event_type === 'error') group.hasError = true;
    if (event.latency_ms) group.totalLatencyMs += event.latency_ms;
  }

  return groups;
}

/** Friendly label for stage name from the backend. */
function formatStageName(stage: string): string {
  const labels: Record<string, string> = {
    intake: 'Case Intake',
    needs_assessment: 'Needs Assessment',
    matching_and_verification: 'Matching & Verification',
    action_planning: 'Action Planning',
    quality_check: 'Quality Check',
    human_review: 'Human Review',
    human_fact_edit: 'Caseworker Fact Edit',
  };
  return labels[stage] ?? stage.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Friendly label for event_type. */
function formatEventType(type: string): string {
  const labels: Record<string, string> = {
    stage_start: 'Stage started',
    stage_complete: 'Stage completed',
    human_checkpoint: 'Human checkpoint',
    tool_call: 'Tool call',
    tool_response: 'Tool response',
    verification: 'Verification',
    retry: 'Retry',
    error: 'Error',
  };
  return labels[type] ?? type.replace(/_/g, ' ');
}

export const TrajectoryView: React.FC<TrajectoryViewProps> = ({ trajectory }) => {
  const groups = groupTrajectoryEvents(trajectory);
  // Open the first group by default
  const [openKey, setOpenKey] = useState<string | null>(groups[0]?.key ?? null);

  const toggle = (key: string) => setOpenKey(openKey === key ? null : key);

  return (
    <Card>
      <SectionHeader
        icon={<Activity className="h-5 w-5" />}
        iconTone="slate"
        title="How MigrantAid Reached This Result"
        description="A traceable view of the assisted analysis stages. Each stage may record multiple internal events — expand to inspect inputs, outputs, and evidence used."
      />

      {groups.length === 0 ? (
        <EmptyState
          icon={<Activity className="h-6 w-6" />}
          title="No trajectory captured yet"
          description="The assisted analysis trace will appear here after a case is processed."
        />
      ) : (
        <ol className="relative space-y-2 pl-1">
          {groups.map((group, idx) => {
            const isOpen = openKey === group.key;
            const isLast = idx === groups.length - 1;
            const isCaseworker = group.agent === 'Caseworker';

            return (
              <li key={group.key} className="relative">
                {!isLast && (
                  <span
                    className="absolute left-3.5 top-9 bottom-[-8px] w-px bg-slate-200"
                    aria-hidden="true"
                  />
                )}

                <div
                  className={cn(
                    'rounded-xl border transition-colors',
                    group.hasError
                      ? 'border-rose-300 bg-rose-50/60'
                      : isOpen
                      ? 'border-brand-200 bg-white'
                      : 'border-slate-200 bg-slate-50/60'
                  )}
                >
                  <button
                    type="button"
                    onClick={() => toggle(group.key)}
                    aria-expanded={isOpen}
                    className="w-full flex items-center gap-3 p-3.5 text-left"
                  >
                    {/* Stage indicator dot */}
                    <span
                      className={cn(
                        'relative flex h-7 w-7 shrink-0 items-center justify-center rounded-full border ring-4 ring-white',
                        group.hasError
                          ? 'bg-rose-500 text-white border-rose-500'
                          : isOpen
                          ? 'bg-brand-600 text-white border-brand-600'
                          : isCaseworker
                          ? 'bg-violet-50 text-violet-600 border-violet-300'
                          : 'bg-white text-slate-500 border-slate-300'
                      )}
                    >
                      {group.hasError ? (
                        <AlertTriangle className="h-4 w-4" aria-hidden="true" />
                      ) : isCaseworker ? (
                        <User className="h-4 w-4" aria-hidden="true" />
                      ) : isOpen ? (
                        <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                      ) : (
                        <Bot className="h-4 w-4" aria-hidden="true" />
                      )}
                    </span>

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                        <span className="text-sm font-semibold text-slate-900">
                          {formatStageName(group.stage)}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {group.agent}
                        </span>
                        {group.hasError && (
                          <span className="text-[10px] bg-rose-100 text-rose-700 px-1.5 py-0.5 rounded font-semibold">
                            Error
                          </span>
                        )}
                        {group.events.length > 1 && (
                          <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                            {group.events.length} events
                          </span>
                        )}
                        {group.events.some((e) => e.retry_count > 0) && (
                          <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-semibold">
                            {Math.max(...group.events.map((e) => e.retry_count))} retr
                            {Math.max(...group.events.map((e) => e.retry_count)) > 1
                              ? 'ies'
                              : 'y'}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-3 mt-0.5 text-[11px] text-slate-400">
                        {group.events[0]?.timestamp && (
                          <span>
                            {new Date(group.events[0].timestamp).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                              second: '2-digit',
                            })}
                          </span>
                        )}
                        {group.totalLatencyMs > 0 && (
                          <span className="inline-flex items-center gap-1">
                            <Clock className="h-3 w-3" aria-hidden="true" />
                            {group.totalLatencyMs.toFixed(0)}ms
                          </span>
                        )}
                      </div>
                    </div>

                    <span className="shrink-0 text-slate-400" aria-hidden="true">
                      {isOpen ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </span>
                  </button>

                  {isOpen && (
                    <div className="px-3.5 pb-3.5 pl-[52px] space-y-2 animate-fade-in">
                      {group.events.map((event, eIdx) => (
                        <div
                          key={eIdx}
                          className="rounded-lg border border-slate-200 bg-slate-50 overflow-hidden"
                        >
                          {/* Sub-event header */}
                          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 border-b border-slate-200">
                            {event.event_type === 'stage_start' ? (
                              <PlayCircle className="h-3 w-3 text-slate-500 shrink-0" aria-hidden="true" />
                            ) : event.event_type === 'stage_complete' ? (
                              <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0" aria-hidden="true" />
                            ) : event.event_type === 'error' ? (
                              <AlertTriangle className="h-3 w-3 text-rose-500 shrink-0" aria-hidden="true" />
                            ) : (
                              <Activity className="h-3 w-3 text-slate-500 shrink-0" aria-hidden="true" />
                            )}
                            <span className="text-[10px] font-semibold text-slate-600 uppercase tracking-wide">
                              {formatEventType(event.event_type)}
                            </span>
                            {event.timestamp && (
                              <span className="text-[10px] text-slate-400 ml-auto">
                                {new Date(event.timestamp).toLocaleTimeString([], {
                                  hour: '2-digit',
                                  minute: '2-digit',
                                  second: '2-digit',
                                })}
                              </span>
                            )}
                            {event.latency_ms != null && (
                              <span className="text-[10px] text-slate-400">
                                {event.latency_ms.toFixed(0)}ms
                              </span>
                            )}
                          </div>

                          {/* Sub-event body */}
                          <div className="p-2.5 space-y-1.5 text-xs">
                            {event.input_summary && (
                              <div>
                                <span className="font-semibold text-slate-600 block mb-0.5">
                                  Input
                                </span>
                                <p className="text-slate-500">{event.input_summary}</p>
                              </div>
                            )}
                            {event.output_summary && (
                              <div>
                                <span className="font-semibold text-slate-700 block mb-0.5">
                                  Output
                                </span>
                                <p className="text-slate-800">{event.output_summary}</p>
                              </div>
                            )}
                            {event.error_message && (
                              <div>
                                <span className="font-semibold text-rose-700 block mb-0.5">
                                  Error
                                </span>
                                <p className="text-rose-600">{event.error_message}</p>
                              </div>
                            )}
                            {!event.input_summary &&
                              !event.output_summary &&
                              !event.error_message && (
                                <p className="text-slate-400">
                                  No additional detail recorded for this event.
                                </p>
                              )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </Card>
  );
};
