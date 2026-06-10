export default function Home() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-24 text-center">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border2 text-xs text-muted mb-8">
        <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
        AI-powered · GitHub native · Free to use
      </div>

      <h1 className="text-5xl font-bold tracking-tight mb-6 leading-tight">
        Professional READMEs,<br />
        <span className="text-accent">pushed to your repo</span>
      </h1>

      <p className="text-lg text-muted mb-10 max-w-xl mx-auto leading-relaxed">
        Paste a GitHub repo URL. ReadmeAI reads every file, estimates the cost, generates a professional README, and pushes it directly after you approve it.
      </p>

      <div className="flex items-center justify-center gap-4">
        <a href="/analyze" className="px-6 py-3 bg-accent text-black font-semibold rounded-lg hover:bg-green-400 transition-all hover:-translate-y-0.5">Generate README</a>
        <a href="https://github.com/joebery/readmeai" target="_blank" className="px-6 py-3 border border-border2 rounded-lg text-muted hover:text-white hover:border-muted transition-all">View on GitHub</a>
      </div>

      <div className="mt-24 grid grid-cols-3 gap-6 text-left">
        <div className="p-5 rounded-xl border border-border bg-surface">
          <div className="text-2xl mb-3">⚡</div>
          <div className="font-semibold mb-1">Instant scan</div>
          <div className="text-sm text-muted leading-relaxed">Reads every file in your repo. No manual config.</div>
        </div>
        <div className="p-5 rounded-xl border border-border bg-surface">
          <div className="text-2xl mb-3">💰</div>
          <div className="font-semibold mb-1">Cost preview</div>
          <div className="text-sm text-muted leading-relaxed">See the token count and exact cost before anything runs.</div>
        </div>
        <div className="p-5 rounded-xl border border-border bg-surface">
          <div className="text-2xl mb-3">✓</div>
          <div className="font-semibold mb-1">You approve first</div>
          <div className="text-sm text-muted leading-relaxed">Preview the README before it ever touches your repo.</div>
        </div>
      </div>
    </div>
  );
}