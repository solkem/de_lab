"use client";

import { useEffect, useState } from "react";

import { apiRequest, type LineageEdge } from "@/lib/api";


export function LineageView() {
  const [edges, setEdges] = useState<LineageEdge[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void apiRequest<LineageEdge[]>("/lineage")
      .then(setEdges)
      .catch((cause) => {
        setError(cause instanceof Error ? cause.message : "Failed to load lineage");
      });
  }, []);

  return (
    <article className="card" style={{ marginTop: 18 }}>
      <p className="eyebrow">Lineage</p>
      <h3 style={{ marginBottom: 8 }}>Recorded source-to-target edges</h3>
      {error ? <p className="error-text">{error}</p> : null}
      {edges.length === 0 ? (
        <p className="muted">Run a pipeline to populate lineage edges.</p>
      ) : (
        <div className="run-stack">
          {edges.map((edge) => (
            <div className="run-card" key={edge.id}>
              <div className="run-meta">
                <strong>{edge.relation_type}</strong>
                <span className="muted">
                  {edge.source_type} -> {edge.target_type}
                </span>
              </div>
              <pre className="run-output">{`${edge.source_name}\n-> ${edge.target_name}`}</pre>
            </div>
          ))}
        </div>
      )}
    </article>
  );
}

