import { useEffect, useState, useCallback } from 'react';

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'migrantaid-theme';

/**
 * Resolves the initial theme synchronously (used by the no-flash init
 * script in _document.tsx and on first client render).
 *
 * Precedence:
 *   1. User's saved preference in localStorage
 *   2. Operating system / browser preference (prefers-color-scheme)
 *   3. Light (safe default)
 */
function resolveInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light';
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved === 'light' || saved === 'dark') return saved;
  } catch {
    /* ignore storage errors */
  }
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === 'dark') root.classList.add('dark');
  else root.classList.remove('dark');
  root.style.colorScheme = theme;
}

/**
 * Light/Dark theme management.
 * - Persists the user's choice across reloads.
 * - Respects the system preference until the user explicitly chooses.
 */
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => resolveInitialTheme());

  // Apply the class to the document and reflect the OS/browser color-scheme.
  // We intentionally do NOT write localStorage here: the system preference is
  // respected until the user explicitly chooses, so a silently-derived value
  // must not override a later system change.
  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((t) => {
      const next = t === 'dark' ? 'light' : 'dark';
      try {
        window.localStorage.setItem(STORAGE_KEY, next);
      } catch {
        /* ignore storage errors */
      }
      return next;
    });
  }, []);

  return { theme, setTheme, toggleTheme };
}
