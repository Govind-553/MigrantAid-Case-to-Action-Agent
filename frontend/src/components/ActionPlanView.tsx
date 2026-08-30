import React from 'react';
import { ListOrdered, CheckSquare, UserCheck, AlertCircle, ArrowRight } from 'lucide-react';
import { ActionPlan, ActionItem } from '../types';

interface ActionPlanViewProps {
  actionPlan: ActionPlan;
}

export const ActionPlanView: React.FC<ActionPlanViewProps> = ({ actionPlan }) => {
  const getPriorityBadge = (priority: ActionItem['priority']) => {
    switch (priority) {
      case 'critical':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
            Critical Step
          </span>
        );
      case 'high':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-100 text-amber-800 border border-amber-200">
            High Priority
          </span>
        );
      case 'medium':
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-blue-100 text-blue-800 border border-blue-200">
            Standard Step
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center space-x-2.5 mb-4 pb-3 border-b border-slate-100">
        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
          <ListOrdered className="h-5 w-5" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-slate-900">Sequential Action Plan</h3>
          <p className="text-xs text-slate-500">
            Prioritized step-by-step instructions for the caseworker and beneficiary with role assignments.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {actionPlan.actions.map((act) => (
          <div
            key={act.step}
            className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors flex items-start space-x-3"
          >
            {/* Step Number Badge */}
            <div className="shrink-0 w-7 h-7 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center shadow-sm">
              {act.step}
            </div>

            {/* Action Details */}
            <div className="space-y-1 flex-1">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-sm font-semibold text-slate-900">{act.action}</span>
                {getPriorityBadge(act.priority)}
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">{act.reason}</p>

              <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] text-slate-500">
                <div className="flex items-center space-x-1">
                  <UserCheck className="h-3.5 w-3.5 text-slate-400" />
                  <span className="capitalize">Role: {act.responsible_role.replace(/_/g, ' ')}</span>
                </div>

                {act.prerequisite && (
                  <div className="flex items-center space-x-1 text-slate-500">
                    <ArrowRight className="h-3 w-3 text-slate-400" />
                    <span>Prerequisite: {act.prerequisite}</span>
                  </div>
                )}

                {act.unresolved_uncertainty && (
                  <div className="flex items-center space-x-1 text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                    <AlertCircle className="h-3 w-3 text-amber-600" />
                    <span>Uncertainty: {act.unresolved_uncertainty}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
