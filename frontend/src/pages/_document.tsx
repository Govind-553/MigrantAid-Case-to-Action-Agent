import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="description" content="MigrantAid — Evidence-backed case-to-action assistant for supporting migrant workers" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <body className="bg-slate-50 antialiased">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
