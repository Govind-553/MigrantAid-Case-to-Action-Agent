import { Html, Head, Main, NextScript } from 'next/document';

const THEME_INIT = `
(function () {
  try {
    var saved = localStorage.getItem('migrantaid-theme');
    var theme = saved === 'light' || saved === 'dark'
      ? saved
      : (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    var root = document.documentElement;
    if (theme === 'dark') root.classList.add('dark');
    root.style.colorScheme = theme;
  } catch (e) {}
})();
`;

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="description" content="MigrantAid — Case-to-action assistant for supporting migrant workers" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" type="image/png" href="/icon.png" />
        <link rel="apple-touch-icon" href="/icon.png" />
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT }} />
      </Head>
      <body className="bg-slate-50 dark:bg-slate-950 antialiased">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
