"use client";

import { useEffect, useState } from "react";

import { API_BASE_URL, apiRequest, type Notebook, type NotebookDetail, type NotebookRun } from "@/lib/api";


const STARTER_NOTEBOOK = {
  name: "Retail Bronze Exploration",
  path: "/Workspace/Starter/Retail Bronze Exploration",
  language: "PYTHON",
  owner: "platform",
};

const STARTER_CODE = `print("LakeForge notebook execution is active")
result = spark.sql("SELECT 1 AS ready")`;


function formatRunOutput(run: NotebookRun): string {
  if (run.error_message) {
    return run.error_message;
  }
  if (!run.output_json) {
    return "No output captured.";
  }
  try {
    return JSON.stringify(JSON.parse(run.output_json), null, 2);
  } catch {
    return run.output_json;
  }
}


export function NotebookWorkbench() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [selectedNotebookId, setSelectedNotebookId] = useState<number | null>(null);
  const [detail, setDetail] = useState<NotebookDetail | null>(null);
  const [code, setCode] = useState(STARTER_CODE);
  const [language, setLanguage] = useState("PYTHON");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadNotebooks(selectNewest = false) {
    try {
      const data = await apiRequest<Notebook[]>("/notebooks");
      setNotebooks(data);
      if (data.length === 0) {
        setSelectedNotebookId(null);
        setDetail(null);
        return;
      }

      const nextId =
        selectNewest || selectedNotebookId === null || !data.some((item) => item.id === selectedNotebookId)
          ? data[0].id
          : selectedNotebookId;
      setSelectedNotebookId(nextId);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to load notebooks");
    }
  }

  async function loadNotebookDetail(notebookId: number) {
    try {
      const data = await apiRequest<NotebookDetail>(`/notebooks/${notebookId}`);
      setDetail(data);
      setLanguage(data.notebook.language);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to load notebook detail");
    }
  }

  useEffect(() => {
    void loadNotebooks();
  }, []);

  useEffect(() => {
    if (selectedNotebookId !== null) {
      void loadNotebookDetail(selectedNotebookId);
    }
  }, [selectedNotebookId]);

  async function ensureStarterNotebook() {
    if (notebooks.length > 0) {
      return;
    }

    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      await apiRequest<Notebook>("/notebooks", {
        method: "POST",
        body: JSON.stringify(STARTER_NOTEBOOK),
      });
      await loadNotebooks(true);
      setMessage("Starter notebook created.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to create starter notebook");
    } finally {
      setBusy(false);
    }
  }

  async function runCell() {
    if (selectedNotebookId === null) {
      setError("Create or select a notebook before running code.");
      return;
    }

    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      await apiRequest<NotebookRun>(`/notebooks/${selectedNotebookId}/execute`, {
        method: "POST",
        body: JSON.stringify({
          language,
          code,
          compute_resource_name: "starter-interactive",
        }),
      });
      await loadNotebookDetail(selectedNotebookId);
      setMessage("Cell execution completed.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Notebook execution failed");
      await loadNotebookDetail(selectedNotebookId);
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className="card" style={{ marginTop: 18 }}>
      <p className="eyebrow">Notebook Workbench</p>
      <h3 style={{ marginBottom: 8 }}>Interactive authoring path</h3>
      <p className="muted" style={{ marginTop: 0 }}>
        API base: {API_BASE_URL}
      </p>

      <div className="workbench-grid">
        <div className="workbench-panel">
          <div className="workbench-toolbar">
            <strong>Notebook</strong>
            <button className="action-button secondary" disabled={busy} onClick={() => void ensureStarterNotebook()}>
              Create Starter
            </button>
          </div>

          <div className="selector-block">
            <label htmlFor="notebook-select">Open notebook</label>
            <select
              id="notebook-select"
              value={selectedNotebookId ?? ""}
              onChange={(event) => setSelectedNotebookId(Number(event.target.value))}
              disabled={notebooks.length === 0}
            >
              {notebooks.length === 0 ? (
                <option value="">No notebooks yet</option>
              ) : (
                notebooks.map((notebook) => (
                  <option key={notebook.id} value={notebook.id}>
                    {notebook.name}
                  </option>
                ))
              )}
            </select>
          </div>

          {detail ? (
            <div className="mini-stack">
              <div className="mini-row">
                <span className="muted">Path</span>
                <strong>{detail.notebook.path}</strong>
              </div>
              <div className="mini-row">
                <span className="muted">Language</span>
                <strong>{detail.notebook.language}</strong>
              </div>
            </div>
          ) : (
            <p className="muted">Create a starter notebook to begin.</p>
          )}
        </div>

        <div className="workbench-panel wide">
          <div className="workbench-toolbar">
            <strong>Cell</strong>
            <div className="inline-controls">
              <select value={language} onChange={(event) => setLanguage(event.target.value)}>
                <option value="PYTHON">PYTHON</option>
                <option value="SQL">SQL</option>
              </select>
              <button className="action-button" disabled={busy || selectedNotebookId === null} onClick={() => void runCell()}>
                {busy ? "Running..." : "Run Cell"}
              </button>
            </div>
          </div>
          <textarea
            className="code-editor"
            value={code}
            onChange={(event) => setCode(event.target.value)}
            spellCheck={false}
          />
          {message ? <p className="success-text">{message}</p> : null}
          {error ? <p className="error-text">{error}</p> : null}
        </div>
      </div>

      <div className="workbench-panel" style={{ marginTop: 18 }}>
        <div className="workbench-toolbar">
          <strong>Recent Runs</strong>
          <span className="muted">{detail?.runs.length ?? 0} run(s)</span>
        </div>

        {!detail || detail.runs.length === 0 ? (
          <p className="muted">Run a cell to populate notebook history.</p>
        ) : (
          <div className="run-stack">
            {detail.runs.map((run) => (
              <div className="run-card" key={run.id}>
                <div className="run-meta">
                  <strong>
                    Run #{run.id} | {run.language} | {run.status}
                  </strong>
                  <span className="muted">{run.compute_resource_name}</span>
                </div>
                <pre className="run-output">{formatRunOutput(run)}</pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}
