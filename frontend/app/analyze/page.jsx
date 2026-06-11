"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import StylePicker from "../../components/StylePicker";

const API = "https://readmeai-production.up.railway.app";

export default function AnalyzePage() {
  const router = useRouter();

  const [repoUrl, setRepoUrl] = useState("");
  const [ghToken, setGhToken] = useState(() => typeof window !== "undefined" ? sessionStorage.getItem("gh_token") || "" : "");
  const [oaiKey, setOaiKey] = useState(() => typeof window !== "undefined" ? sessionStorage.getItem("oai_key") || "" : "");
  const [style, setStyle] = useState("professional");
  const [styleUrl, setStyleUrl] = useState("");

  const [estimate, setEstimate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState("");

  function saveTokens() {
    sessionStorage.setItem("gh_token", ghToken);
    sessionStorage.setItem("oai_key", oaiKey);
  }

  async function handleEstimate() {
    setError("");
    setEstimate(null);
    if (!repoUrl || !ghToken || !oaiKey) {
      setError("Please fill in all fields.");
      return;
    }
    setLoading(true);
    saveTokens();
    try {
      const res = await fetch(`${API}/api/v1/analyses/estimate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: repoUrl,
          github_token: ghToken,
          style: style === "custom" ? null : style,
          style_url: style === "custom" ? styleUrl : null,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Estimate failed");
      setEstimate(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm() {
    setError("");
    setConfirming(true);
    try {
      const res = await fetch(`${API}/api/v1/analyses`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          analysis_id: estimate.analysis_id,
          github_token: ghToken,
          openai_key: oaiKey,
          confirmed: true,
          style: style === "custom" ? null : style,
          style_url: style === "custom" ? styleUrl : null,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to start generation");
      router.push(`/analyses/${data.id}`);
    } catch (e) {
      setError(e.message);
      setConfirming(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-16">
      <div className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Generate README</h1>
        <p className="text-muted">Paste your repo URL, add your keys, pick a style.</p>
      </div>

      <div className="space-y-5">
        <div>
          <label className="block text-xs uppercase tracking-widest text-muted mb-2">GitHub Repository URL</label>
          <input
            type="text"
            value={repoUrl}
            onChange={e => setRepoUrl(e.target.value)}
            placeholder="https://github.com/username/repository"
            className="w-full px-4 py-3 bg-surface border border-border2 rounded-lg font-mono text-sm outline-none focus:border-accent transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs uppercase tracking-widest text-muted mb-2">GitHub Personal Access Token</label>
          <input
            type="password"
            value={ghToken}
            onChange={e => setGhToken(e.target.value)}
            placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxx"
            className="w-full px-4 py-3 bg-surface border border-border2 rounded-lg font-mono text-sm outline-none focus:border-accent transition-colors"
          />
          <p className="text-xs text-muted mt-1">Needs <code className="bg-surface2 px-1 rounded">repo</code> scope. <a href="https://github.com/settings/tokens" target="_blank" className="text-accent2 hover:underline">Create one</a></p>
        </div>

        <div>
          <label className="block text-xs uppercase tracking-widest text-muted mb-2">OpenAI API Key</label>
          <input
            type="password"
            value={oaiKey}
            onChange={e => setOaiKey(e.target.value)}
            placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
            className="w-full px-4 py-3 bg-surface border border-border2 rounded-lg font-mono text-sm outline-none focus:border-accent transition-colors"
          />
          <p className="text-xs text-muted mt-1">Used only for this generation. <a href="https://platform.openai.com/api-keys" target="_blank" className="text-accent2 hover:underline">Get your key</a></p>
        </div>

        <StylePicker style={style} setStyle={setStyle} styleUrl={styleUrl} setStyleUrl={setStyleUrl} />
      </div>

      {error && (
        <div className="mt-6 px-4 py-3 bg-red-950 border border-red-800 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {!estimate && (
        <button
          onClick={handleEstimate}
          disabled={loading}
          className="mt-8 w-full py-3 bg-accent text-black font-semibold rounded-lg hover:bg-green-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Scanning repo..." : "Estimate →"}
        </button>
      )}

      {estimate && (
        <div className="mt-8 p-6 bg-surface border border-border2 rounded-xl">
          <div className="text-sm text-muted uppercase tracking-widest mb-4">Estimate</div>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <div className="text-2xl font-bold">{estimate.file_count}</div>
              <div className="text-xs text-muted mt-1">Total files</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{estimate.filtered_file_count}</div>
              <div className="text-xs text-muted mt-1">Files to read</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{estimate.estimated_input_tokens.toLocaleString()}</div>
              <div className="text-xs text-muted mt-1">Input tokens</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-accent">${estimate.estimated_cost_usd.toFixed(4)}</div>
              <div className="text-xs text-muted mt-1">Estimated cost</div>
            </div>
          </div>

          <div className="text-xs text-muted mb-5 p-3 bg-surface2 rounded-lg">
            Model: <span className="text-white font-mono">{estimate.model}</span> · Repo: <span className="text-white font-mono">{estimate.repo_full_name}</span>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleConfirm}
              disabled={confirming}
              className="flex-1 py-3 bg-accent text-black font-semibold rounded-lg hover:bg-green-400 transition-all disabled:opacity-50"
            >
              {confirming ? "Starting..." : "Confirm & Generate →"}
            </button>
            <button
              onClick={() => setEstimate(null)}
              className="px-5 py-3 border border-border2 rounded-lg text-muted hover:text-white hover:border-muted transition-all"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}