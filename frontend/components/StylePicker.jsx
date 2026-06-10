"use client";

const PRESETS = [
  { id: "minimal", label: "Minimal", desc: "Clean, no emojis, brief" },
  { id: "professional", label: "Professional", desc: "Badges, tables, formal" },
  { id: "opensource", label: "Open Source", desc: "Community focused" },
  { id: "portfolio", label: "Portfolio", desc: "Job seeker friendly" },
  { id: "startup", label: "Startup", desc: "Product marketing tone" },
  { id: "custom", label: "Copy a style", desc: "Match any GitHub repo" },
];

export default function StylePicker({ style, setStyle, styleUrl, setStyleUrl }) {
  return (
    <div>
      <label className="block text-xs uppercase tracking-widest text-muted mb-2">README Style</label>
      <div className="grid grid-cols-3 gap-2 mb-3">
        {PRESETS.map(p => (
          <button
            key={p.id}
            onClick={() => setStyle(p.id)}
            className={`p-3 rounded-lg border text-left transition-all ${style === p.id ? "border-accent bg-surface2" : "border-border bg-surface hover:border-border2"}`}
          >
            <div className="text-sm font-medium">{p.label}</div>
            <div className="text-xs text-muted mt-0.5">{p.desc}</div>
          </button>
        ))}
      </div>

      {style === "custom" && (
        <div className="mt-2">
          <label className="block text-xs uppercase tracking-widest text-muted mb-2">GitHub Repo to copy style from</label>
          <input
            type="text"
            value={styleUrl}
            onChange={e => setStyleUrl(e.target.value)}
            placeholder="https://github.com/sindresorhus/awesome"
            className="w-full px-4 py-3 bg-surface border border-border2 rounded-lg font-mono text-sm outline-none focus:border-accent transition-colors"
          />
          <p className="text-xs text-muted mt-1">We fetch this repo's README and match its tone, structure, and style.</p>
        </div>
      )}
    </div>
  );
}