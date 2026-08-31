import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
  details?: string;
}

/**
 * Friendly error state. Never exposes stack traces/raw JSON by default;
 * technical details are hidden behind a collapsible disclosure.
 */
export const ErrorState: React.FC<ErrorStateProps> = ({
  message,
  onRetry,
  retryLabel = 'Try Again',
  details,
}) => {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="bg-danger.bg border border-danger.border rounded-xl p-6">
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-danger shrink-0 mt-0.5" aria-hidden="true" />
        <div className="min-w-0">
          <p className="text-sm font-semibold text-danger.text">{message}</p>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
            Please try again. Your previous work has not been lost.
          </p>

          {(onRetry || details) && (
            <div className="mt-3 flex items-center gap-2">
              {onRetry && (
                <Button variant="secondary" size="sm" onClick={onRetry}>
                  {retryLabel}
                </Button>
              )}
              {details && (
                <button
                  type="button"
                  onClick={() => setShowDetails((v) => !v)}
                  className="inline-flex items-center gap-1 text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                  aria-expanded={showDetails}
                >
                  Technical details
                  {showDetails ? (
                    <ChevronUp className="h-3.5 w-3.5" aria-hidden="true" />
                  ) : (
                    <ChevronDown className="h-3.5 w-3.5" aria-hidden="true" />
                  )}
                </button>
              )}
            </div>
          )}

          {showDetails && details && (
            <pre className="mt-3 p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-[11px] text-slate-600 dark:text-slate-300 overflow-auto max-h-40">
              {details}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};
