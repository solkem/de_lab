import { JobsWorkbench } from "@/components/jobs-workbench";
import { Sidebar } from "@/components/sidebar";


export default function JobsPage() {
  return (
    <main className="app-shell">
      <div className="frame">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark" />
            <div className="brand-copy">
              <h1>LakeForge</h1>
              <p>Jobs orchestration workspace</p>
            </div>
          </div>
          <div className="status-pill">Notebook jobs active</div>
        </header>

        <div className="layout">
          <Sidebar activeItem="Jobs" />
          <section className="content">
            <div className="hero">
              <article className="card">
                <p className="eyebrow">Jobs Surface</p>
                <h2>First orchestration path</h2>
                <p className="muted">
                  This page lets us package notebook execution as a reusable job, trigger runs,
                  and inspect run history through a jobs-oriented control plane.
                </p>
              </article>

              <article className="card">
                <p className="eyebrow">What It Covers</p>
                <h3>Notebook task jobs and run history</h3>
                <p className="muted">
                  It is a focused first slice, but it mirrors the key mental model behind
                  Databricks Jobs: define a task, attach compute, run it, and inspect outcomes.
                </p>
              </article>
            </div>

            <JobsWorkbench />
          </section>
        </div>
      </div>
    </main>
  );
}
