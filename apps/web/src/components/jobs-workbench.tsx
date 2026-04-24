"use client";

import { useEffect, useMemo, useState } from "react";

import { apiRequest, type Job, type JobDetail, type Notebook } from "@/lib/api";


const DEFAULT_JOB_CODE = `print("LakeForge job execution is active")
result = spark.sql("SELECT current_timestamp() AS run_ts")`;


export function JobsWorkbench() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [detail, setDetail] = useState<JobDetail | null>(null);
  const [jobName, setJobName] = useState("starter-notebook-job");
  const [notebookId, setNotebookId] = useState<number | null>(null);
  const [language, setLanguage] = useState("PYTHON");
  const [code, setCode] = useState(DEFAULT_JOB_CODE);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadNotebooks() {
    const data = await apiRequest<Notebook[]>("/notebooks");
    setNotebooks(data);
    if (data.length > 0 && notebookId === null) {
      setNotebookId(data[0].id);
    }
  }

  async function loadJobs(selectNewest = false) {
    const data = await apiRequest<Job[]>("/jobs");
    setJobs(data);
    if (data.length === 0) {
      setSelectedJobId(null);
      setDetail(null);
      return;
    }

    const nextId =
      selectNewest || selectedJobId === null || !data.some((job) => job.id === selectedJobId)
        ? data[0].id
        : selectedJobId;
    setSelectedJobId(nextId);
  }

  async function loadJobDetail(jobId: number) {
    const data = await apiRequest<JobDetail>(`/jobs/${jobId}`);
    setDetail(data);
  }

  useEffect(() => {
    async function boot() {
      try {
        await loadNotebooks();
        await loadJobs();
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : "Failed to load jobs workspace");
      }
    }
    void boot();
  }, []);

  useEffect(() => {
    if (selectedJobId !== null) {
      void loadJobDetail(selectedJobId).catch((cause) => {
        setError(cause instanceof Error ? cause.message : "Failed to load job detail");
      });
    }
  }, [selectedJobId]);

  const selectedNotebook = useMemo(
    () => notebooks.find((item) => item.id === notebookId) ?? null,
    [notebooks, notebookId],
  );

  async function createJob() {
    if (notebookId === null) {
      setError("Create a notebook first from the notebook workbench.");
      return;
    }

    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      await apiRequest<Job>("/jobs", {
        method: "POST",
        body: JSON.stringify({
          name: jobName,
          notebook_id: notebookId,
          compute_resource_name: "starter-interactive",
          language,
          code,
          owner: "platform",
        }),
      });
      await loadJobs(true);
      setMessage("Job created.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to create job");
    } finally {
      setBusy(false);
    }
  }

  async function runJob() {
    if (selectedJobId === null) {
      setError("Create or select a job before running it.");
      return;
    }

    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      await apiRequest(`/jobs/${selectedJobId}/run`, { method: "POST" });
      await loadJobDetail(selectedJobId);
      setMessage("Job run completed.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to run job");
      await loadJobDetail(selectedJobId).catch(() => undefined);
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className="card" style={{ marginTop: 18 }}>
      <p className="eyebrow">Jobs Workbench</p>
      <h3 style={{ marginBottom: 8 }}>Notebook job orchestration</h3>
      <div className="workbench-grid">
        <div className="workbench-panel">
          <div className="workbench-toolbar">
            <strong>Create Job</strong>
          </div>

          <div className="selector-block">
            <label htmlFor="job-name">Job name</label>
            <input id="job-name" value={jobName} onChange={(event) => setJobName(event.target.value)} />
          </div>

          <div className="selector-block">
            <label htmlFor="job-notebook">Notebook</label>
            <select
              id="job-notebook"
              value={notebookId ?? ""}
              onChange={(event) => setNotebookId(Number(event.target.value))}
              disabled={notebooks.length === 0}
            >
              {notebooks.length === 0 ? (
                <option value="">No notebooks available</option>
              ) : (
                notebooks.map((notebook) => (
                  <option key={notebook.id} value={notebook.id}>
                    {notebook.name}
                  </option>
                ))
              )}
            </select>
          </div>

          <div className="selector-block">
            <label htmlFor="job-language">Language</label>
            <select id="job-language" value={language} onChange={(event) => setLanguage(event.target.value)}>
              <option value="PYTHON">PYTHON</option>
              <option value="SQL">SQL</option>
            </select>
          </div>

          <button className="action-button" disabled={busy || notebookId === null} onClick={() => void createJob()}>
            {busy ? "Working..." : "Create Job"}
          </button>

          {selectedNotebook ? (
            <div className="mini-stack">
              <div className="mini-row">
                <span className="muted">Notebook path</span>
                <strong>{selectedNotebook.path}</strong>
              </div>
            </div>
          ) : null}
        </div>

        <div className="workbench-panel wide">
          <div className="workbench-toolbar">
            <strong>Task code</strong>
            <button className="action-button secondary" disabled={busy || selectedJobId === null} onClick={() => void runJob()}>
              Run Selected Job
            </button>
          </div>
          <textarea className="code-editor" value={code} onChange={(event) => setCode(event.target.value)} spellCheck={false} />
          {message ? <p className="success-text">{message}</p> : null}
          {error ? <p className="error-text">{error}</p> : null}
        </div>
      </div>

      <div className="workbench-grid" style={{ marginTop: 18 }}>
        <div className="workbench-panel">
          <div className="workbench-toolbar">
            <strong>Jobs</strong>
          </div>
          <div className="selector-block">
            <label htmlFor="job-select">Open job</label>
            <select
              id="job-select"
              value={selectedJobId ?? ""}
              onChange={(event) => setSelectedJobId(Number(event.target.value))}
              disabled={jobs.length === 0}
            >
              {jobs.length === 0 ? (
                <option value="">No jobs yet</option>
              ) : (
                jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.name}
                  </option>
                ))
              )}
            </select>
          </div>

          {detail ? (
            <div className="mini-stack">
              <div className="mini-row">
                <span className="muted">Task type</span>
                <strong>{detail.job.task_type}</strong>
              </div>
              <div className="mini-row">
                <span className="muted">Compute</span>
                <strong>{detail.job.compute_resource_name}</strong>
              </div>
              <div className="mini-row">
                <span className="muted">Notebook</span>
                <strong>{detail.notebook.name}</strong>
              </div>
            </div>
          ) : (
            <p className="muted">Create a job to begin orchestration practice.</p>
          )}
        </div>

        <div className="workbench-panel wide">
          <div className="workbench-toolbar">
            <strong>Recent Job Runs</strong>
            <span className="muted">{detail?.runs.length ?? 0} run(s)</span>
          </div>
          {!detail || detail.runs.length === 0 ? (
            <p className="muted">Run a job to populate execution history.</p>
          ) : (
            <div className="run-stack">
              {detail.runs.map((run) => (
                <div className="run-card" key={run.id}>
                  <div className="run-meta">
                    <strong>
                      Job Run #{run.id} | {run.status}
                    </strong>
                    <span className="muted">{new Date(run.created_at).toLocaleString()}</span>
                  </div>
                  <pre className="run-output">
                    {run.error_message ? run.error_message : run.output_json ?? "No output captured."}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </article>
  );
}

