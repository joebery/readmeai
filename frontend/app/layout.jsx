import "./globals.css";

export const metadata = {
  title: "ReadmeAI",
  description: "AI-generated READMEs pushed directly to your GitHub repo",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-bg text-gray-100 font-sans">
        <nav className="border-b border-border px-6 py-4 flex items-center justify-between">
          <a href="/" className="flex items-baseline gap-1">
            <span className="text-xl font-bold tracking-tight">Readme</span>
            <span className="text-xl font-bold tracking-tight text-accent">AI</span>
          </a>
          <div className="flex items-center gap-6 text-sm text-muted">
            <a href="/analyze" className="hover:text-white transition-colors">Generate</a>
            <a href="https://github.com/joebery/readmeai" target="_blank" className="hover:text-white transition-colors">GitHub</a>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}