import React, { useState, useEffect, useRef } from 'react';
import {
  ShieldCheck,
  BarChart3,
  Users,
  Menu,
  X,
  Activity,
  Info,
  CheckCircle2,
  Sun,
  Moon,
} from 'lucide-react';
import { cn } from '@/lib/cn';
import { useTheme } from '@/lib/useTheme';

interface HeaderProps {
  currentTab: 'casework' | 'benchmark';
  onTabChange: (tab: 'casework' | 'benchmark') => void;
}

const TABS = [
  { id: 'casework' as const, label: 'Casework Workspace', icon: Users },
  { id: 'benchmark' as const, label: 'VARR Benchmark', icon: BarChart3 },
];

const GROUNDED_RULES_POINTS = [
  'Eligibility is evaluated against structured requirements from the approved resource knowledge base.',
  'Unknown information stays UNKNOWN — it is never promoted to eligible.',
  'Missing information is flagged for follow-up, not treated as a passing condition.',
  'The LLM extracts facts and explains steps — it does not override verification rules.',
  'Human review is required before any consequential referral progression.',
];

const PROVENANCE = [
  { label: 'Knowledge Base', value: 'Approved Resource KB' },
  { label: 'Verification', value: 'Deterministic Rule Engine' },
  { label: 'Unknown values', value: 'Preserved (UNKNOWN ≠ eligible)' },
  { label: 'Resource KB version', value: 'v1.0' },
  { label: 'Human review', value: 'Required before referral action' },
];

const GroundedRulesContent: React.FC = () => {
  return (
    <div
      role="dialog"
      aria-modal="false"
      aria-label="Grounded Rules explanation"
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-card-lg z-50 overflow-hidden"
    >
      {/* Header */}
      <div className="px-4 pt-4 pb-3 border-b border-slate-100 dark:border-slate-800 bg-brand-50 dark:bg-brand-950/40">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-brand-600 dark:text-brand-400" aria-hidden="true" />
          <h2 className="text-xs font-bold text-brand-900 dark:text-brand-200 uppercase tracking-wide">
            Grounded Rules Active
          </h2>
        </div>
        <p className="text-[11px] text-brand-700 dark:text-brand-300 mt-1 leading-relaxed">
          Eligibility decisions are grounded in explicit resource rules and
          deterministic verification logic — not LLM inference.
        </p>
      </div>

      {/* Safety properties */}
      <ul className="px-4 py-3 space-y-2">
        {GROUNDED_RULES_POINTS.map((point, i) => (
          <li key={i} className="flex items-start gap-2 text-[11px] text-slate-700 dark:text-slate-300">
            <CheckCircle2
              className="h-3.5 w-3.5 text-emerald-500 shrink-0 mt-0.5"
              aria-hidden="true"
            />
            <span>{point}</span>
          </li>
        ))}
      </ul>

      {/* Provenance table */}
      <div className="mx-4 mb-3 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
        <table className="w-full text-[11px]">
          <tbody>
            {PROVENANCE.map((row, i) => (
              <tr
                key={i}
                className={cn(
                  'border-b border-slate-100 dark:border-slate-800 last:border-0',
                  i % 2 === 0 ? 'bg-slate-50 dark:bg-slate-800/40' : 'bg-white dark:bg-slate-900'
                )}
              >
                <td className="px-2.5 py-1.5 font-semibold text-slate-500 dark:text-slate-400 whitespace-nowrap">
                  {row.label}
                </td>
                <td className="px-2.5 py-1.5 text-slate-800 dark:text-slate-200">{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Disclaimer */}
      <div className="px-4 pb-4">
        <p className="text-[10px] text-slate-400 dark:text-slate-500 leading-relaxed italic">
          &ldquo;Grounded rules support caseworker decision-making; they do not replace
          official eligibility determination.&rdquo;
        </p>
      </div>
    </div>
  );
};

export const Header: React.FC<HeaderProps> = ({ currentTab, onTabChange }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [rulesOpen, setRulesOpen] = useState(false);
  const [mobileRulesOpen, setMobileRulesOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const rulesRef = useRef<HTMLDivElement>(null);
  const rulesBtnRef = useRef<HTMLButtonElement>(null);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
      if (
        rulesRef.current &&
        !rulesRef.current.contains(e.target as Node) &&
        rulesBtnRef.current &&
        !rulesBtnRef.current.contains(e.target as Node)
      ) {
        setRulesOpen(false);
      }
    }
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        setMenuOpen(false);
        setRulesOpen(false);
        setMobileRulesOpen(false);
      }
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
    <header className="bg-white/95 dark:bg-slate-900/95 backdrop-blur border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-3">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3 min-w-0">
            <div className="bg-brand-600 p-2 rounded-lg text-white shadow-card shrink-0">
              <ShieldCheck className="h-6 w-6" aria-hidden="true" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-slate-900 dark:text-white tracking-tight truncate">
                  MigrantAid
                </span>
                <span className="hidden lg:inline-flex bg-brand-50 dark:bg-brand-950/50 text-brand-700 dark:text-brand-300 text-[11px] font-semibold px-2 py-0.5 rounded-full border border-brand-200 dark:border-brand-800 whitespace-nowrap">
                  Case-to-Action
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 hidden xl:block truncate">
                Evidence-backed caseworker assistant for migrant workers &amp; families
              </p>
            </div>
          </div>

          {/* Desktop tab nav + grounded rules + theme toggle */}
          <div className="hidden md:flex items-center gap-3">
            <nav className="flex space-x-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg" aria-label="Workspace">
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
                        ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                        : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
                    )}
                  >
                    <Icon className="h-4 w-4" aria-hidden="true" />
                    <span className="whitespace-nowrap">{tab.label}</span>
                  </button>
                );
              })}
            </nav>

            {/* Grounded Rules — interactive indicator (md+ tablet/desktop; compact so it never overflows) */}
            <div className="relative hidden md:block">
              <button
                ref={rulesBtnRef}
                type="button"
                onClick={() => setRulesOpen((v) => !v)}
                aria-expanded={rulesOpen}
                aria-haspopup="dialog"
                title="Click to learn how MigrantAid grounds eligibility decisions"
                className={cn(
                  'flex items-center gap-1.5 text-xs bg-slate-50 dark:bg-slate-800 border px-2.5 py-1.5 rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
                  rulesOpen
                    ? 'border-brand-400 text-brand-700 dark:text-brand-300 bg-brand-50 dark:bg-brand-950/50'
                    : 'border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-600 hover:text-slate-700 dark:hover:text-slate-100'
                )}
              >
                <Activity
                  className={cn(
                    'h-3.5 w-3.5 shrink-0',
                    rulesOpen ? 'text-brand-600 dark:text-brand-400' : 'text-brand-600 dark:text-brand-400 animate-pulse'
                  )}
                  aria-hidden="true"
                />
                <span className="font-medium whitespace-nowrap">Grounded Rules Active</span>
                <Info className="h-3 w-3 opacity-60 shrink-0" aria-hidden="true" />
              </button>

              {/* Popover panel */}
              {rulesOpen && (
                <div ref={rulesRef} className="absolute right-0 top-full mt-2 w-80 max-w-[calc(100vw-2rem)]">
                  <GroundedRulesContent />
                  <button
                    type="button"
                    onClick={() => setRulesOpen(false)}
                    className="absolute top-3 right-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 rounded"
                    aria-label="Close grounded rules panel"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>

            {/* Theme toggle (desktop) */}
            <ThemeToggleButton theme={theme} onToggle={toggleTheme} />
          </div>

          {/* Mobile: theme toggle + menu button */}
          <div className="md:hidden flex items-center gap-2">
            <ThemeToggleButton theme={theme} onToggle={toggleTheme} />
            <button
              type="button"
              onClick={() => setMenuOpen((v) => !v)}
              aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
              aria-expanded={menuOpen}
              className="inline-flex items-center justify-center h-10 w-10 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
            >
              {menuOpen ? (
                <X className="h-5 w-5" aria-hidden="true" />
              ) : (
                <Menu className="h-5 w-5" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div ref={menuRef} className="md:hidden border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-card-lg">
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
                      ? 'bg-brand-50 dark:bg-brand-950/50 text-brand-800 dark:text-brand-200 ring-1 ring-brand-200 dark:ring-brand-800'
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
                  )}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  {tab.label}
                </button>
              );
            })}

            {/* Grounded Rules — interactive in mobile menu */}
            <div className="pt-2 mt-1 border-t border-slate-100 dark:border-slate-800">
              <button
                type="button"
                onClick={() => setMobileRulesOpen((v) => !v)}
                aria-expanded={mobileRulesOpen}
                aria-haspopup="dialog"
                className="flex w-full items-center gap-2 px-3 py-2.5 rounded-lg text-xs text-brand-700 dark:text-brand-300 hover:bg-brand-50 dark:hover:bg-brand-950/50 transition-colors text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
              >
                <Activity className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400 animate-pulse shrink-0" aria-hidden="true" />
                <span className="font-medium">Grounded Rules Active</span>
                <span className="ml-auto text-slate-400 dark:text-slate-500">
                  {mobileRulesOpen ? 'Hide' : 'Learn more'}
                </span>
              </button>
              {mobileRulesOpen && (
                <div className="mt-1">
                  <GroundedRulesContent />
                </div>
              )}
            </div>
          </nav>
        </div>
      )}
    </header>
  );
};

interface ThemeToggleButtonProps {
  theme: 'light' | 'dark';
  onToggle: () => void;
}

const ThemeToggleButton: React.FC<ThemeToggleButtonProps> = ({ theme, onToggle }) => {
  const isDark = theme === 'dark';
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className="inline-flex items-center justify-center h-10 w-10 shrink-0 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
    >
      {isDark ? (
        <Sun className="h-5 w-5" aria-hidden="true" />
      ) : (
        <Moon className="h-5 w-5" aria-hidden="true" />
      )}
    </button>
  );
};
