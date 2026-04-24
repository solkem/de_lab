# LakeForge

LakeForge is a Databricks-like Data Engineering practice platform. This repository contains the Phase 1 foundation:

- `apps/api`: FastAPI control plane
- `apps/web`: Next.js workspace shell
- `infra`: local platform infrastructure

## Phase 1 goals

- local object storage with MinIO
- metadata database with Postgres
- local Spark runtime for future Delta execution
- control-plane API for health, catalog metadata, compute, and table registration
- workspace shell UI
- local development setup through Docker Compose

## Repo layout

```text
lakeforge/
  apps/
    api/
    web/
  infra/
  docs/
```

## Quick start

1. Start local infrastructure:

```powershell
docker compose up -d postgres minio createbuckets spark-master spark-worker
```

2. Run the API from `apps/api`.

3. Run the web app from `apps/web`.

Implementation now includes pipeline expectations and persisted lineage edges, with a simple lineage page in the web app and run-level quality detail in the pipeline surface. Next we can deepen pipeline semantics with richer expectation engines, system tables, and incremental flow behavior.
