import React from 'react';
import { Activity, Clock, CheckCircle2, Bot, ArrowDown } from 'lucide-react';
import { AgentEvent } from '../types';

interface TrajectoryViewProps {
  trajectory: AgentEvent[];
}

export const TrajectoryView: React.FC<TrajectoryViewProps> = ({ trajectory }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center space-x-2.5 mb-4 pb-3 border-b border-slate-100">
        <div className="p-2 bg-slate-100 text-slate-700 rounded-lg">
          <Activity className="h-5 w-5" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-slate-900">Observable Agent Trajectory</h3>
          <p className="text-xs text-slate-500">
            Chronological log of multi-agent events, latencies, and intermediate state transformations.
          </p>
        </div>
      </div>

      <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {trajectory.map((event, idx) => (
          <div key={idx} className="relative">
            {/* Step dot */}
            <div className="absolute -left-6 top-1 w-3 h-3 rounded-full bg-emerald-500 ring-4 ring-white" />

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Bot className="h-3.5 w-3.5 text-slate-600" />
                  <span className="font-bold text-slate-900">{event.agent}</span>
                  <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded text-slate-700 font-mono uppercase">
                    {event.stage}
                  </span>
                </div>
                {event.latency_ms !== null && event.latency_ms !== undefined && (
                  <span className="text-[11px] text-slate-500 font-mono">
                    {event.latency_ms.toFixed(1)}ms
                  </span>
                )}
              </div>

              {event.input_summary && (
                <p className="text-slate-600 text-[11px]">
                  <strong className="text-slate-700">Input:</strong> {event.input_summary}
                </p>
              )}

              {event.output_summary && (
                <p className="text-slate-800 text-[11px]">
                  <strong className="text-slate-700">Output:</strong> {event.output_summary}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
