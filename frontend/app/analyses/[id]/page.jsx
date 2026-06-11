"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import ReadmeComparison from "../../../components/ReadmeComparison";

const API = "https://readmeai-production.up.railway.app";

export default function AnalysisPage() {
  const { id } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [pushing, setPushing] = useState(false);
  const [pushed, setPushed] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [regenerating, setRegenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const ghToken = typeof window !== "undefined" ? sessionStorage.getItem("gh_token") || "" : "";
  const oaiKey = typeof window !== "undefined" ? sessionStorage.getItem("oai_key") || "" : "";

  useEffect(() => {
    if (!id) return;
    const poll = setInterval(async () => {
      try {
        const res = await fetch(`${API}/api/v1/analyses/${id}`);
        const data = await res.json();
        setAnalysis(data);
        if (["confirming", "complete", "failed"].includes(data.status)) {
          clearInterval(poll);
        }
      } catch (e) {
        setError("Failed to fetch analysis status");
        clearInterval(poll);
      }
    }, 3000);
    return () => clearInterval(poll);
  }, [id]);

  async function handlePush() {
    setPushing(true);
    try {
      const res = await fetch(`${API}/api/v1/analyses/${id}/push`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ github_token: ghToken }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Push failed");
      setAnalysis(data);
      setPushed(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setPushing(false);
    }
  }

  async function handleRegenerate() {
    setRegenerating(true);
    setShowFeedback(false);
    try {
      const res = await fetch(`${API}/api/v1/analyses/${id}/regenerate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          github_token: ghToken,
          openai_key: oaiKey,
          feedback: feedback || null,
          style: analysis?.style || null,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Regenerate failed");
      setAnalysis(data);
      setFeedback("");
      const poll = setInterval(async () => {
        const r = await fetch(`${API}/api/v1/analyses/${id}`);
        const d = await r.json();
        setAnalysis(d);
        if (["confirming", "complete", "failed"].includes(d.status)) {
          clearInterval(poll);
          setRegenerating(false);
        }
      }, 3000);
    } catch (e) {
      setError(e.message);
      setRegenerating(false);
    }
  }

  async function handleDiscard() {
    await fetch(`${API}/api/v1/analyses/${id}`, { method: "DELETE" });
    window.location.href = "/analyze";
  }

  function handleCopy() {
    navigator.clipboard.writeText(analysis?.readme_content || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const isGenerating = analysis && ["queued", "generating", "scanning"].includes(analysis.status);
  const isReady = analysis?.status === "confirming";
  const isComplete = analysis?.status === "complete";

  return (
    <div className="w-full max-w-[1400px] mx-auto px-4 md:px-8 py-12">
      {!analysis && !error && (
        <div className="text-center py-24">
          <div className="w-8 h-8 border-2 border-border2 border-t-accent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted">Connecting...</p>
        </div>
      )}

      {error && (
        <div className="px-4 py-3 bg-red-950 border border-red-800 rounded-lg text-red-400 text-sm mb-6">
          {error}
        </div>
      )}

      {analysis && (
        <>
          <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight mb-1">README Preview</h1>
              <p className="text-sm text-muted">Review before pushing to GitHub</p>
            </div>
            <div className="flex items-center gap-3">
              <button onClick={handleCopy} className="text-xs px-3 py-2 border border-border2 rounded-lg text-muted hover:text-white hover:border-muted transition-all">
                {copied ? "Copied!" : "Copy markdown"}
              </button>
              <StatusBadge status={analysis.status} />
            </div>
          </div>

          {isGenerating && (
            <div className="text-center py-16 border border-border rounded-xl bg-surface">
              <div className="w-8 h-8 border-2 border-border2 border-t-accent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-muted capitalize">{analysis.status}...</p>
              <p className="text-xs text-muted mt-2">This usually takes 15-30 seconds</p>
            </div>
          )}

          {(isReady || isComplete) && analysis.readme_content && (
            <>
              <div className="mb-8">
                <ReadmeComparison
                  previousReadme={analysis.previous_readme || ""}
                  newReadme={analysis.readme_content}
                />
              </div>

              {isReady && !pushed && (
                <>
                  {showFeedback && (
                    <div className="mb-4 p-4 bg-surface border border-border2 rounded-xl">
                      <label className="block text-xs uppercase tracking-widest text-muted mb-2">What would you like to change?</label>
                      <textarea
                        value={feedback}
                        onChange={e => setFeedback(e.target.value)}
                        placeholder="e.g. Add more detail to the installation section, include environment variable descriptions..."
                        className="w-full px-3 py-2 bg-surface2 border border-border2 rounded-lg text-sm outline-none focus:border-accent transition-colors resize-none h-24"
                      />
                      <p className="text-xs text-muted mt-2">Regenerating will cost an additional ~${analysis.estimated_cost_usd || "0.003"}</p>
                      <div className="flex gap-3 mt-3">
                        <button onClick={handleRegenerate} disabled={regenerating} className="px-4 py-2 bg-accent text-black text-sm font-semibold rounded-lg hover:bg-green-400 transition-all disabled:opacity-50">
                          {regenerating ? "Regenerating..." : "Regenerate"}
                        </button>
                        <button onClick={() => setShowFeedback(false)} className="px-4 py-2 border border-border2 rounded-lg text-sm text-muted hover:text-white transition-all">
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-3 flex-wrap">
                    {ghToken ? (
                    <button onClick={handlePush} disabled={pushing} className="flex-1 min-w-[160px] py-3 bg-accent text-black font-semibold rounded-lg hover:bg-green-400 transition-all disabled:opacity-50">
                        {pushing ? "Pushing..." : "Push to GitHub →"}
                    </button>
                    ) : (
                    <button onClick={handleCopy} className="flex-1 min-w-[160px] py-3 bg-accent text-black font-semibold rounded-lg hover:bg-green-400 transition-all">
                        {copied ? "Copied! ✓" : "Copy README markdown"}
                    </button>
                    )}
                    <button onClick={() => setShowFeedback(!showFeedback)} className="px-5 py-3 border border-border2 rounded-lg text-muted hover:text-white hover:border-muted transition-all">
                      Regenerate
                    </button>
                    <button onClick={handleDiscard} className="px-5 py-3 border border-red-900 rounded-lg text-red-400 hover:bg-red-950 transition-all">
                      Discard
                    </button>
                  </div>
                </>
              )}

              {(isComplete || pushed) && analysis.commit_url && (
                <div className="flex items-center gap-4 p-4 bg-surface border border-accent border-opacity-30 rounded-xl mt-6">
                  <span className="text-accent text-xl">✓</span>
                  <div>
                    <div className="font-semibold text-sm">README pushed successfully</div>
                    <a href={analysis.commit_url} target="_blank" className="text-xs text-accent2 hover:underline font-mono">{analysis.commit_url}</a>
                  </div>
                </div>
              )}

              {analysis.status === "failed" && (
                <div className="p-4 bg-red-950 border border-red-800 rounded-xl text-red-400 text-sm mt-6">
                  {analysis.error_message || "Generation failed"}
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

function StatusBadge({ status }) {
  const colours = {
    queued: "bg-yellow-950 text-yellow-400 border-yellow-800",
    scanning: "bg-blue-950 text-blue-400 border-blue-800",
    generating: "bg-blue-950 text-blue-400 border-blue-800",
    confirming: "bg-green-950 text-green-400 border-green-800",
    pushing: "bg-blue-950 text-blue-400 border-blue-800",
    complete: "bg-green-950 text-green-400 border-green-800",
    failed: "bg-red-950 text-red-400 border-red-800",
  };
  return (
    <span className={`px-3 py-1 rounded-full border text-xs font-medium capitalize ${colours[status] || ""}`}>
      {status}
    </span>
  );
}