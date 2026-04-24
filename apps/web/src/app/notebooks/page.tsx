import { Sidebar } from "@/components/sidebar";
import { NotebookWorkbench } from "@/components/notebook-workbench";


export default function NotebooksPage() {
  return (
    <main className="app-shell">
      <div className="frame">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark" />
            <div className="brand-copy">
              <h1>LakeForge</h1>
              <p>Notebook authoring workspace</p>
            </div>
          </div>
          <div className="status-pill">Notebook workbench active</div>
        </header>

        <div className="layout">
          <Sidebar activeItem="Notebooks" />
          <section className="content">
            <div className="hero">
              <article className="card">
                <p className="eyebrow">Notebook Surface</p>
                <h2>First interactive execution path</h2>
                <p className="muted">
                  This page lets us create a starter notebook, run SQL or Python code against
                  the backend API, and inspect run history like a lightweight Databricks-style
                  authoring loop.
                </p>
              </article>

              <article className="card">
                <p className="eyebrow">What It Covers</p>
                <h3>Notebook metadata, execution, and run history</h3>
                <p className="muted">
                  It is intentionally small, but it gives us a real product path from editor to
                  execution result, which is the right base for richer notebooks later.
                </p>
              </article>
            </div>

            <NotebookWorkbench />
          </section>
        </div>
      </div>
    </main>
  );
}
