import React, { useState, useEffect, useRef } from 'react';
import { ShieldCheck, BarChart3, Users, Menu, X, Activity } from 'lucide-react';
import { cn } from '@/lib/cn';

interface HeaderProps {
  currentTab: 'casework' | 'benchmark';
  onTabChange: (tab: 'casework' | 'benchmark') => void;
}

const TABS = [
  { id: 'casework' as const, label: 'Casework Workspace', icon: Users },
  { id: 'benchmark' as const, label: 'VARR Benchmark', icon: BarChart3 },
];

export const Header: React.FC<HeaderProps> = ({ currentTab, onTabChange }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setMenuOpen(false);
    }
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKey);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKey);
    };
  }, []);

  const selectTab = (tab: 'casework' | 'benchmark') => {
    onTabChange(tab);
    setMenuOpen(false);
  };

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3 min-w-0">
            <div className="bg-brand-600 p-2 rounded-lg text-white shadow-card shrink-0">
              <ShieldCheck className="h-6 w-6" aria-hidden="true" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-slate-900 tracking-tight truncate">
                  MigrantAid
                </span>
                <span className="hidden sm:inline-flex bg-brand-50 text-brand-700 text-[11px] font-semibold px-2 py-0.5 rounded-full border border-brand-200 whitespace-nowrap">
                  Case-to-Action
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden sm:block truncate">
                Evidence-backed caseworker assistant for migrant workers &amp; families
              </p>
            </div>
          </div>

          {/* Desktop tab nav */}
          <div className="hidden md:flex items-center gap-4">
            <nav className="flex space-x-1 bg-slate-100 p-1 rounded-lg" aria-label="Workspace">
              {TABS.map((tab) => {
                const Icon = tab.icon;
                const active = currentTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => onTabChange(tab.id)}
                    aria-current={active ? 'page' : undefined}
                    className={cn(
                      'flex items-center gap-2 px-3.5 py-1.5 rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
                      active
                        ? 'bg-white text-slate-900 shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    )}
                  >
                    <Icon className="h-4 w-4" aria-hidden="true" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>

            <div className="hidden xl:flex items-center gap-1.5 text-xs text-slate-500 bg-slate-50 border border-slate-200 px-2.5 py-1.5 rounded-md">
              <Activity className="h-3.5 w-3.5 text-brand-600 animate-pulse" aria-hidden="true" />
              <span>Grounded Rules Active</span>
            </div>
          </div>

          {/* Mobile menu button */}
          <button
            type="button"
            onClick={() => setMenuOpen((v) => !v)}
            aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={menuOpen}
            className="md:hidden inline-flex items-center justify-center h-10 w-10 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
          >
            {menuOpen ? (
              <X className="h-5 w-5" aria-hidden="true" />
            ) : (
              <Menu className="h-5 w-5" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div ref={menuRef} className="md:hidden border-t border-slate-200 bg-white shadow-card">
          <nav className="px-4 py-3 space-y-1" aria-label="Workspace mobile">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const active = currentTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => selectTab(tab.id)}
                  aria-current={active ? 'page' : undefined}
                  className={cn(
                    'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                    active
                      ? 'bg-brand-50 text-brand-800 ring-1 ring-brand-200'
                      : 'text-slate-700 hover:bg-slate-50'
                  )}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      )}
    </header>
  );
};
