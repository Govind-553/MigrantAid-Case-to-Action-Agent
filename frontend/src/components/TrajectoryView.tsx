import React, { useState } from 'react';
import { Activity, Bot, CheckCircle2, ChevronDown, ChevronUp, Clock } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { EmptyState } from '@/components/ui/EmptyState';
import { AgentEvent } from '@/types';
import { cn } from '@/lib/cn';

interface TrajectoryViewProps {
  trajectory: AgentEvent[];
}

export const TrajectoryView: React.FC<TrajectoryViewProps> = ({ trajectory }) => {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  const toggle = (idx: number) => setOpenIdx(openIdx === idx ? null : idx);

  return (
    <Card>
      <SectionHeader
        icon={<Activity className="h-5 w-5" />}
        iconTone="slate"
        title="How MigrantAid Reached This Result"
        description="A traceable view of the assisted analysis stages. Expand any stage to inspect what happened and the evidence used."
      />

      {trajectory.length === 0 ? (
        <EmptyState
          icon={<Activity className="h-6 w-6" />}
          title="No trajectory captured yet"
          description="The assisted analysis trace will appear here after a case is processed."
        />
      ) : (
        <ol className="relative space-y-2 pl-1">
          {trajectory.map((event, idx) => {
            const isOpen = openIdx === idx;
            const isLast = idx === trajectory.length - 1;

            return (
              <li key={idx} className="relative">
                {!isLast && (
                  <span
                    className="absolute left-3.5 top-9 bottom-[-8px] w-px bg-slate-200"
                    aria-hidden="true"
                  />
                )}

                <div
                  className={cn(
                    'rounded-xl border transition-colors',
                    isOpen ? 'border-brand-200 bg-white' : 'border-slate-200 bg-slate-50/60'
                  )}
                >
                  <button
                    type="button"
                    onClick={() => toggle(idx)}
                    aria-expanded={isOpen}
                    className="w-full flex items-center gap-3 p-3.5 text-left"
                  >
                    {/* Stage indicator */}
                    <span
                      className={cn(
                        'relative flex h-7 w-7 shrink-0 items-center justify-center rounded-full border ring-4 ring-white',
                        isOpen
                          ? 'bg-brand-600 text-white border-brand-600'
                          : 'bg-white text-slate-500 border-slate-300'
                      )}
                    >
                      {isOpen ? (
                        <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                      ) : (
                        <Bot className="h-4 w-4" aria-hidden="true" />
                      )}
                    </span>

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                        <span className="text-sm font-semibold text-slate-900 capitalize">
                          {event.agent.replace(/_/g, ' ')}
                        </span>
                        {event.stage && (
                          <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded text-slate-700 font-mono uppercase">
                            {event.stage}
                          </span>
                        )}
                        {event.retry_count > 0 && (
                          <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-semibold">
                            {event.retry_count} retr{event.retry_count > 1 ? 'ies' : 'y'}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-3 mt-0.5 text-[11px] text-slate-400">
                        {event.timestamp && (
                          <span>
                            {new Date(event.timestamp).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                              second: '2-digit',
                            })}
                          </span>
                        )}
                        {event.latency_ms !== null && event.latency_ms !== undefined && (
                          <span className="inline-flex items-center gap-1">
                            <Clock className="h-3 w-3" aria-hidden="true" />
                            {event.latency_ms.toFixed(0)}ms
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
                      {event.input_summary && (
                        <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs">
                          <span className="font-semibold text-slate-700 block mb-0.5">
                            Input
                          </span>
                          <p className="text-slate-600">{event.input_summary}</p>
                        </div>
                      )}
                      {event.output_summary && (
                        <div className="p-2.5 bg-white rounded-lg border border-slate-200 text-xs">
                          <span className="font-semibold text-slate-700 block mb-0.5">
                            Output
                          </span>
                          <p className="text-slate-800">{event.output_summary}</p>
                        </div>
                      )}
                      {!event.input_summary && !event.output_summary && (
                        <p className="text-xs text-slate-400">
                          Stage completed. No additional detail recorded for this prototype.
                        </p>
                      )}
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
