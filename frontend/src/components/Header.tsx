import React from 'react';
import { ShieldCheck, Activity, BarChart3, Users } from 'lucide-react';

interface HeaderProps {
  currentTab: 'casework' | 'benchmark';
  onTabChange: (tab: 'casework' | 'benchmark') => void;
}

export const Header: React.FC<HeaderProps> = ({ currentTab, onTabChange }) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3">
            <div className="bg-emerald-600 p-2 rounded-lg text-white shadow-sm">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold text-slate-900 tracking-tight">MigrantAid</span>
                <span className="bg-emerald-100 text-emerald-800 text-xs font-semibold px-2 py-0.5 rounded-full border border-emerald-300">
                  Case-to-Action
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Evidence-backed caseworker assistant for migrant workers & families
              </p>
            </div>
          </div>

          {/* Navigation & Status */}
          <div className="flex items-center space-x-4">
            <nav className="flex space-x-1 bg-slate-100 p-1 rounded-lg">
              <button
                onClick={() => onTabChange('casework')}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  currentTab === 'casework'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Users className="h-4 w-4" />
                <span>Casework Workspace</span>
              </button>
              <button
                onClick={() => onTabChange('benchmark')}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  currentTab === 'benchmark'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
                <span>VARR Benchmark (Baseline vs Agent)</span>
              </button>
            </nav>

            <div className="hidden lg:flex items-center space-x-1.5 text-xs text-slate-500 bg-slate-50 border border-slate-200 px-2.5 py-1.5 rounded-md">
              <Activity className="h-3.5 w-3.5 text-emerald-600 animate-pulse" />
              <span>Grounded Rules Active</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
