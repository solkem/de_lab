import { PipelinesWorkbench } from "@/components/pipelines-workbench";
import { Sidebar } from "@/components/sidebar";


export default function PipelinesPage() {
  return (
    <main className="app-shell">
      <div className="frame">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark" />
            <div className="brand-copy">
              <h1>LakeForge</h1>
              <p>Pipelines workspace</p>
            </div>
          </div>
          <div className="status-pill">Declarative pipelines active</div>
        </header>

        <div className="layout">
          <Sidebar activeItem="Pipelines" />
          <section className="content">
            <div className="hero">
              <article className="card">
                <p className="eyebrow">Pipelines Surface</p>
                <h2>First declarative flow path</h2>
                <p className="muted">
                  This page lets us define notebook-backed pipelines with target catalogs and schemas,
                  trigger runs, and inspect execution history through a pipeline-first control plane.
                </p>
              </article>

              <article className="card">
                <p className="eyebrow">What It Covers</p>
                <h3>Notebook-backed medallion pipeline runs</h3>
                <p className="muted">
                  It is a focused first slice, but it mirrors the Lakeflow-style mental model:
                  define a managed flow, assign a target, run it, and observe outcomes.
                </p>
              </article>
            </div>

            <PipelinesWorkbench />
          </section>
        </div>
      </div>
    </main>
  );
}
