import React from 'react';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center text-center py-10 px-4">
      {icon && (
        <div
          className="mb-3 p-3 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500"
          aria-hidden="true"
        >
          {icon}
        </div>
      )}
      <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{title}</p>
      {description && (
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
};
