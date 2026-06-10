"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import ReactDiffViewer from "react-diff-viewer-continued";

export default function ReadmeComparison({ previousReadme, newReadme }) {
  const [mode, setMode] = useState("preview");
  const [showColors, setShowColors] = useState(true);

  if (!previousReadme || previousReadme.trim() === "") {
    return (
      <div className="border border-border rounded-xl overflow-hidden">
        <div className="px-4 py-3 bg-surface border-b border-border flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent"></span>
          <span className="text-xs text-muted font-mono">README.md — New</span>
        </div>
        <div className="p-8 bg-bg markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{newReadme}</ReactMarkdown>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-1 p-1 bg-surface border border-border rounded-lg">
          <button
            onClick={() => setMode("preview")}
            className={`px-4 py-1.5 rounded text-sm font-medium transition-all ${mode === "preview" ? "bg-surface2 text-white" : "text-muted hover:text-white"}`}
          >
            Preview
          </button>
          <button
            onClick={() => setMode("diff")}
            className={`px-4 py-1.5 rounded text-sm font-medium transition-all ${mode === "diff" ? "bg-surface2 text-white" : "text-muted hover:text-white"}`}
          >
            Diff
          </button>
        </div>

        {mode === "diff" && (
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <div onClick={() => setShowColors(!showColors)} className={`w-9 h-5 rounded-full transition-colors relative cursor-pointer ${showColors ? "bg-accent" : "bg-border2"}`}>
              <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${showColors ? "translate-x-4" : "translate-x-0.5"}`}></div>
            </div>
            <span className="text-xs text-muted">Highlight changes</span>
          </label>
        )}
      </div>

      {/* Preview mode */}
      {mode === "preview" && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div className="border border-border rounded-xl overflow-hidden">
            <div className="px-4 py-3 bg-surface border-b border-border flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-muted"></span>
              <span className="text-xs text-muted font-mono">Current on GitHub</span>
            </div>
            <div className="p-8 bg-bg markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{previousReadme}</ReactMarkdown>
            </div>
          </div>

          <div className="border border-border rounded-xl overflow-hidden" style={{borderColor: "rgba(61,232,122,0.25)"}}>
            <div className="px-4 py-3 bg-surface border-b border-border flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-accent"></span>
              <span className="text-xs text-muted font-mono">New Version</span>
              <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-surface2 border border-border2 text-accent">Generated</span>
            </div>
            <div className="p-8 bg-bg markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{newReadme}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}

      {/* Diff mode */}
      {mode === "diff" && (
        <div className="rounded-xl overflow-hidden border border-border font-mono text-xs">
          <ReactDiffViewer
            oldValue={previousReadme}
            newValue={newReadme}
            splitView={true}
            useDarkTheme={true}
            leftTitle="Current on GitHub"
            rightTitle="New Version"
            showDiffOnly={false}
            styles={{
              contentText: { wordBreak: "break-word", whiteSpace: "pre-wrap" },
              variables: {
                dark: {
                  diffViewerBackground: "#0a0c10",
                  diffViewerColor: "#e8eaf0",
                  addedBackground: showColors ? "#0d1f14" : "#0a0c10",
                  addedColor: "#3de87a",
                  removedBackground: showColors ? "#1f0e0e" : "#0a0c10",
                  removedColor: "#ff5f57",
                  wordAddedBackground: showColors ? "#1a4025" : "transparent",
                  wordRemovedBackground: showColors ? "#3d1010" : "transparent",
                  addedGutterBackground: "#0a1a0f",
                  removedGutterBackground: "#1a0a0a",
                  gutterBackground: "#10141c",
                  gutterBackgroundDark: "#0a0c10",
                  highlightBackground: "#1e2636",
                  highlightGutterBackground: "#161b26",
                  codeFoldGutterBackground: "#161b26",
                  codeFoldBackground: "#10141c",
                  emptyLineBackground: "#0a0c10",
                  gutterColor: "#6b7a99",
                  addedGutterColor: "#3de87a",
                  removedGutterColor: "#ff5f57",
                  codeFoldContentColor: "#6b7a99",
                  diffViewerTitleBackground: "#161b26",
                  diffViewerTitleColor: "#e8eaf0",
                  diffViewerTitleBorderColor: "#1e2636",
                },
              },
            }}
          />
        </div>
      )}
    </div>
  );
}