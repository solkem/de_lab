import { Sidebar } from "@/components/sidebar";
import {
  starterCatalogs,
  starterCompute,
  starterJobs,
  starterNotebooks,
  starterPipelines,
  workspaceSummary,
} from "@/lib/workspace-data";


export default function Home() {
  return (
    <main className="app-shell">
      <div className="frame">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark" />
            <div className="brand-copy">
              <h1>LakeForge</h1>
              <p>Databricks-like Data Engineering practice workspace</p>
            </div>
          </div>
          <div className="status-pill">Phase 6 quality and lineage foundation active</div>
        </header>

        <div className="layout">
          <Sidebar activeItem="Workspace" />

          <section className="content">
            <div className="hero">
              <article className="card">
                <p className="eyebrow">Workspace</p>
                <h2>{workspaceSummary.workspace}</h2>
                <p className="muted">
                  The control plane, object storage, and catalog foundation are now scaffolded.
                  Notebook execution can now be packaged into jobs and pipelines with quality checks and lineage edges.
                  Next we can deepen scheduling, richer expectations, and system observability.
                </p>
              </article>

              <article className="card">
                <p className="eyebrow">Roadmap Focus</p>
                <h3>Pipeline quality checks and lineage tracking</h3>
                <p className="muted">
                  This milestone adds expectations and lineage records so managed flows can be
                  validated and traced through a Databricks-like governance lens.
                </p>
              </article>
            </div>

            <div className="card-grid">
              <article className="card">
                <p className="metric">{workspaceSummary.catalogs}</p>
                <h3>Catalogs</h3>
                <p className="muted">`main` and `system` are seeded by the API on startup.</p>
              </article>

              <article className="card">
                <p className="metric">{workspaceSummary.compute}</p>
                <h3>Compute Profiles</h3>
                <p className="muted">Interactive compute starts as a UI shell in Phase 1.</p>
              </article>

              <article className="card">
                <p className="metric">{workspaceSummary.jobs}</p>
                <h3>Jobs</h3>
                <p className="muted">Notebook task jobs now have a creation and run-history path.</p>
              </article>

              <article className="card">
                <p className="metric">{workspaceSummary.tables}</p>
                <h3>Registered Tables</h3>
                <p className="muted">Managed tables now have a real Delta materialization path.</p>
              </article>

              <article className="card">
                <p className="metric">{workspaceSummary.notebooks}</p>
                <h3>Notebook Assets</h3>
                <p className="muted">SQL and Python notebook execution now has a backend path.</p>
              </article>
            </div>

            <article className="card" style={{ marginTop: 18 }}>
              <p className="eyebrow">Seeded Catalogs</p>
              <div className="table-list">
                {starterCatalogs.map((catalog) => (
                  <div className="table-item" key={catalog.name}>
                    <strong>{catalog.name}</strong>
                    <span className="muted">{catalog.description}</span>
                  </div>
                ))}
              </div>
            </article>

            <article className="card" style={{ marginTop: 18 }}>
              <p className="eyebrow">Compute Foundation</p>
              <div className="table-list">
                {starterCompute.map((compute) => (
                  <div className="table-item" key={compute.name}>
                    <strong>{compute.name}</strong>
                    <span className="muted">
                      {compute.type} | {compute.runtime} | {compute.status}
                    </span>
                  </div>
                ))}
              </div>
            </article>

            <article className="card" style={{ marginTop: 18 }}>
              <p className="eyebrow">Starter Notebooks</p>
              <div className="table-list">
                {starterNotebooks.map((notebook) => (
                  <div className="table-item" key={notebook.path}>
                    <strong>{notebook.name}</strong>
                    <span className="muted">
                      {notebook.language} | {notebook.path}
                    </span>
                  </div>
                ))}
              </div>
            </article>

            <article className="card" style={{ marginTop: 18 }}>
              <p className="eyebrow">Starter Jobs</p>
              <div className="table-list">
                {starterJobs.map((job) => (
                  <div className="table-item" key={job.name}>
                    <strong>{job.name}</strong>
                    <span className="muted">
                      {job.type} | {job.compute}
                    </span>
                  </div>
                ))}
              </div>
            </article>

            <article className="card" style={{ marginTop: 18 }}>
              <p className="eyebrow">Starter Pipelines</p>
              <div className="table-list">
                {starterPipelines.map((pipeline) => (
                  <div className="table-item" key={pipeline.name}>
                    <strong>{pipeline.name}</strong>
                    <span className="muted">
                      {pipeline.mode} | {pipeline.target}
                    </span>
                  </div>
                ))}
              </div>
            </article>

            <article className="card" style={{ marginTop: 18 }}>
              <p className="eyebrow">Next Click</p>
              <h3 style={{ marginBottom: 8 }}>Open the notebook workbench</h3>
              <p className="muted" style={{ marginTop: 0 }}>
                The first interactive authoring, orchestration, pipeline, and lineage pages are now available at `/notebooks`, `/jobs`, `/pipelines`, and `/lineage`.
              </p>
              <div className="inline-controls">
                <a className="action-link" href="/notebooks">
                  Go To Notebooks
                </a>
                <a className="action-link" href="/jobs">
                  Go To Jobs
                </a>
                <a className="action-link" href="/pipelines">
                  Go To Pipelines
                </a>
                <a className="action-link" href="/lineage">
                  Go To Lineage
                </a>
              </div>
            </article>
          </section>
        </div>
      </div>
    </main>
  );
}
