"use client";

import { useEffect, useMemo, useState } from "react";

import {
  apiRequest,
  type LineageEdge,
  type Notebook,
  type Pipeline,
  type PipelineDetail,
  type PipelineExpectation,
  type PipelineExpectationResult,
  type PipelineRunDetail,
} from "@/lib/api";


const DEFAULT_PIPELINE_CODE = `print("LakeForge pipeline execution is active")
result = spark.sql("SELECT 'bronze_to_silver' AS flow_stage")`;


export function PipelinesWorkbench() {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [selectedPipelineId, setSelectedPipelineId] = useState<number | null>(null);
  const [detail, setDetail] = useState<PipelineDetail | null>(null);
  const [pipelineName, setPipelineName] = useState("starter-medallion-pipeline");
  const [notebookId, setNotebookId] = useState<number | null>(null);
  const [language, setLanguage] = useState("PYTHON");
  const [code, setCode] = useState(DEFAULT_PIPELINE_CODE);
  const [targetCatalog, setTargetCatalog] = useState("main");
  const [targetSchema, setTargetSchema] = useState("silver");
  const [mode, setMode] = useState("BATCH");
  const [targetTable, setTargetTable] = useState("silver_orders");
  const [expectations, setExpectations] = useState<PipelineExpectation[]>([
    { name: "preview_rows_present", constraint_sql: "row_count_preview >= 1", action: "WARN" },
    { name: "dataframe_output", constraint_sql: "output_type = 'dataframe'", action: "WARN" },
  ]);
  const [runDetail, setRunDetail] = useState<PipelineRunDetail | null>(null);
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

  async function loadPipelines(selectNewest = false) {
    const data = await apiRequest<Pipeline[]>("/pipelines");
    setPipelines(data);
    if (data.length === 0) {
      setSelectedPipelineId(null);
      setDetail(null);
      return;
    }

    const nextId =
      selectNewest || selectedPipelineId === null || !data.some((item) => item.id === selectedPipelineId)
        ? data[0].id
        : selectedPipelineId;
    setSelectedPipelineId(nextId);
  }

  async function loadPipelineDetail(pipelineId: number) {
    const data = await apiRequest<PipelineDetail>(`/pipelines/${pipelineId}`);
    setDetail(data);
    if (data.runs.length > 0) {
      const latestRun = await apiRequest<PipelineRunDetail>(`/pipelines/runs/${data.runs[0].id}`);
      setRunDetail(latestRun);
    } else {
      setRunDetail(null);
    }
  }

  useEffect(() => {
    async function boot() {
      try {
        await loadNotebooks();
        await loadPipelines();
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : "Failed to load pipelines workspace");
      }
    }
    void boot();
  }, []);

  useEffect(() => {
    if (selectedPipelineId !== null) {
      void loadPipelineDetail(selectedPipelineId).catch((cause) => {
        setError(cause instanceof Error ? cause.message : "Failed to load pipeline detail");
      });
    }
  }, [selectedPipelineId]);

  const selectedNotebook = useMemo(
    () => notebooks.find((item) => item.id === notebookId) ?? null,
    [notebooks, notebookId],
  );

  async function createPipeline() {
    if (notebookId === null) {
      setError("Create a notebook first from the notebook workbench.");
      return;
    }

    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      await apiRequest<Pipeline>("/pipelines", {
        method: "POST",
        body: JSON.stringify({
          name: pipelineName,
          notebook_id: notebookId,
          compute_resource_name: "starter-interactive",
          language,
          code,
          target_catalog: targetCatalog,
          target_schema: targetSchema,
          target_table: targetTable,
          mode,
          expectations,
          owner: "platform",
        }),
      });
      await loadPipelines(true);
      setMessage("Pipeline created.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to create pipeline");
    } finally {
      setBusy(false);
    }
  }

  async function runPipeline() {
    if (selectedPipelineId === null) {
      setError("Create or select a pipeline before running it.");
      return;
    }

    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      await apiRequest(`/pipelines/${selectedPipelineId}/run`, { method: "POST" });
      await loadPipelineDetail(selectedPipelineId);
      setMessage("Pipeline run completed.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Failed to run pipeline");
      await loadPipelineDetail(selectedPipelineId).catch(() => undefined);
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className="card" style={{ marginTop: 18 }}>
      <p className="eyebrow">Pipelines Workbench</p>
      <h3 style={{ marginBottom: 8 }}>Declarative notebook-backed flows</h3>
      <div className="workbench-grid">
        <div className="workbench-panel">
          <div className="workbench-toolbar">
            <strong>Create Pipeline</strong>
          </div>

          <div className="selector-block">
            <label htmlFor="pipeline-name">Pipeline name</label>
            <input id="pipeline-name" value={pipelineName} onChange={(event) => setPipelineName(event.target.value)} />
          </div>

          <div className="selector-block">
            <label htmlFor="pipeline-notebook">Notebook</label>
            <select
              id="pipeline-notebook"
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
            <label htmlFor="pipeline-mode">Mode</label>
            <select id="pipeline-mode" value={mode} onChange={(event) => setMode(event.target.value)}>
              <option value="BATCH">BATCH</option>
              <option value="CONTINUOUS">CONTINUOUS</option>
            </select>
          </div>

          <div className="workbench-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
            <div className="selector-block">
              <label htmlFor="target-catalog">Target catalog</label>
              <input id="target-catalog" value={targetCatalog} onChange={(event) => setTargetCatalog(event.target.value)} />
            </div>
            <div className="selector-block">
              <label htmlFor="target-schema">Target schema</label>
              <input id="target-schema" value={targetSchema} onChange={(event) => setTargetSchema(event.target.value)} />
            </div>
          </div>

          <div className="selector-block">
            <label htmlFor="target-table">Target table</label>
            <input id="target-table" value={targetTable} onChange={(event) => setTargetTable(event.target.value)} />
          </div>

          <button className="action-button" disabled={busy || notebookId === null} onClick={() => void createPipeline()}>
            {busy ? "Working..." : "Create Pipeline"}
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
            <strong>Pipeline code</strong>
            <div className="inline-controls">
              <select value={language} onChange={(event) => setLanguage(event.target.value)}>
                <option value="PYTHON">PYTHON</option>
                <option value="SQL">SQL</option>
              </select>
              <button className="action-button secondary" disabled={busy || selectedPipelineId === null} onClick={() => void runPipeline()}>
                Run Selected Pipeline
              </button>
            </div>
          </div>
          <textarea className="code-editor" value={code} onChange={(event) => setCode(event.target.value)} spellCheck={false} />
          {message ? <p className="success-text">{message}</p> : null}
          {error ? <p className="error-text">{error}</p> : null}
        </div>
      </div>

      <div className="workbench-grid" style={{ marginTop: 18 }}>
        <div className="workbench-panel">
          <div className="workbench-toolbar">
            <strong>Pipelines</strong>
          </div>
          <div className="selector-block">
            <label htmlFor="pipeline-select">Open pipeline</label>
            <select
              id="pipeline-select"
              value={selectedPipelineId ?? ""}
              onChange={(event) => setSelectedPipelineId(Number(event.target.value))}
              disabled={pipelines.length === 0}
            >
              {pipelines.length === 0 ? (
                <option value="">No pipelines yet</option>
              ) : (
                pipelines.map((pipeline) => (
                  <option key={pipeline.id} value={pipeline.id}>
                    {pipeline.name}
                  </option>
                ))
              )}
            </select>
          </div>

          {detail ? (
            <div className="mini-stack">
              <div className="mini-row">
                <span className="muted">Mode</span>
                <strong>{detail.pipeline.mode}</strong>
              </div>
              <div className="mini-row">
                <span className="muted">Target</span>
                <strong>
                  {detail.pipeline.target_catalog}.{detail.pipeline.target_schema}.{detail.pipeline.target_table}
                </strong>
              </div>
              <div className="mini-row">
                <span className="muted">Notebook</span>
                <strong>{detail.notebook.name}</strong>
              </div>
            </div>
          ) : (
            <p className="muted">Create a pipeline to begin medallion-flow practice.</p>
          )}
        </div>

        <div className="workbench-panel wide">
          <div className="workbench-toolbar">
            <strong>Recent Pipeline Runs</strong>
            <span className="muted">{detail?.runs.length ?? 0} run(s)</span>
          </div>
          {!detail || detail.runs.length === 0 ? (
            <p className="muted">Run a pipeline to populate execution history.</p>
          ) : (
            <div className="run-stack">
              {detail.runs.map((run) => (
                <div className="run-card" key={run.id}>
                  <div className="run-meta">
                    <strong>
                      Pipeline Run #{run.id} | {run.status}
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

      <div className="workbench-grid" style={{ marginTop: 18 }}>
        <div className="workbench-panel">
          <div className="workbench-toolbar">
            <strong>Expectations</strong>
            <span className="muted">{expectations.length} rule(s)</span>
          </div>
          <div className="run-stack">
            {expectations.map((expectation) => (
              <div className="run-card" key={expectation.name}>
                <div className="run-meta">
                  <strong>{expectation.name}</strong>
                  <span className="muted">{expectation.action}</span>
                </div>
                <pre className="run-output">{expectation.constraint_sql}</pre>
              </div>
            ))}
          </div>
        </div>

        <div className="workbench-panel wide">
          <div className="workbench-toolbar">
            <strong>Latest Quality And Lineage</strong>
            <span className="muted">{runDetail ? `Run #${runDetail.run.id}` : "No run yet"}</span>
          </div>

          {!runDetail ? (
            <p className="muted">Run a pipeline to capture expectation results and lineage edges.</p>
          ) : (
            <div className="run-stack">
              {runDetail.expectation_results.map((result) => (
                <div className="run-card" key={result.id}>
                  <div className="run-meta">
                    <strong>{result.expectation_name}</strong>
                    <span className="muted">
                      {result.status} | {result.action}
                    </span>
                  </div>
                  <pre className="run-output">{`${result.constraint_sql}\n${result.detail ?? ""}`.trim()}</pre>
                </div>
              ))}
              {runDetail.lineage_edges.map((edge) => (
                <div className="run-card" key={`lineage-${edge.id}`}>
                  <div className="run-meta">
                    <strong>{edge.relation_type}</strong>
                    <span className="muted">{edge.source_type} -> {edge.target_type}</span>
                  </div>
                  <pre className="run-output">{`${edge.source_name}\n-> ${edge.target_name}`}</pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
