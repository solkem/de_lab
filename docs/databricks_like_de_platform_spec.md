# Databricks-Like Data Engineering Practice Platform Spec

## 1. Objective

Design a Data Engineering practice platform that is as close as realistically possible to the Databricks Data Engineering experience while remaining buildable as an open, local-first platform for hands-on practice.

This platform is not meant to clone Databricks commercially. It is meant to reproduce the engineering workflow that strong Data Engineers actually use on Databricks:

- land data into a lakehouse
- organize data with medallion layers
- write batch and streaming transformations
- manage Delta tables
- orchestrate jobs and pipelines
- apply data quality rules
- inspect lineage and run history
- work through notebooks, SQL, and Git-backed projects
- observe platform metadata through system tables

Working name for the practice platform: `LakeForge`.

## 2. What Databricks DE Actually Is

Based on current Databricks documentation reviewed on April 23, 2026, the Data Engineering experience is centered around a few tightly integrated platform ideas:

### 2.1 Lakehouse foundation

Databricks positions the platform around the lakehouse model, with Delta Lake as the default table format and medallion architecture as the recommended design pattern.

Important implications:

- storage and compute are separated
- Delta tables are the default operational unit
- the same data can serve batch, streaming, and SQL use cases
- bronze, silver, and gold are first-class mental models for DE work

### 2.2 Governance-first metadata plane

Unity Catalog is not just a metastore. It is the control plane for:

- catalogs, schemas, tables, views, volumes
- permissions
- lineage
- discovery and metadata
- quality and monitoring tie-ins

In practice, serious Databricks DE work is built around `catalog.schema.table` naming and governed access.

### 2.3 Multiple compute modes

Databricks exposes several compute experiences:

- serverless compute for notebooks, workflows, and pipelines
- classic compute for configurable clusters
- SQL warehouses for SQL analytics

That means the user experience is not "run Spark manually"; it is "pick a compute resource and execute."

### 2.4 Notebook-first but not notebook-only

Databricks notebooks remain a primary authoring tool, with support for Python, SQL, Scala, and R, real-time collaboration, visualizations, and versioning. But production workflows also rely on:

- Python scripts
- SQL files
- Git folders
- declarative bundles
- jobs and pipelines APIs

### 2.5 Jobs + declarative pipelines

Databricks separates orchestration from transformation logic:

- Lakeflow Jobs orchestrates DAG-style workflows and scheduled tasks
- Lakeflow Spark Declarative Pipelines provides declarative batch/streaming pipelines with streaming tables, materialized views, expectations, and managed incremental logic

### 2.6 Ingestion, quality, lineage, observability

For DE, the platform experience includes:

- Auto Loader for incremental file ingestion
- expectations for row-level quality constraints in pipelines
- Unity Catalog lineage down to column level
- system tables for usage, billing, compute, query, and lineage observability

## 3. Reverse-Engineered Databricks Capability Model

To practice for tough DE roles, these are the capabilities we should reproduce with the highest fidelity.

### Tier A: Must feel like Databricks

- Delta-based lakehouse tables
- catalog/schema/table object model
- notebook + SQL authoring
- job orchestration with task DAGs
- pipeline abstraction for batch and streaming
- medallion architecture workflow
- table history and time travel
- data quality expectations
- lineage graph
- run history and operational observability

### Tier B: Important platform realism

- interactive compute vs job compute vs SQL warehouse mental model
- RBAC and grants
- Git-integrated project workflow
- environment promotion and deployment bundles
- ingestion checkpoints and schema evolution
- cluster policies / compute profiles

### Tier C: Nice to have, but not required for training value

- true multi-tenant SaaS isolation
- Databricks proprietary performance layers such as Photon
- full enterprise IAM/networking controls
- full cloud-region/serverless control plane behavior
- complete Unity Catalog feature parity

## 4. Design Principles For Our Platform

### 4.1 Optimize for skill transfer

If a user practices on this platform, the workflows should transfer to Databricks interviews and real projects with minimal translation.

### 4.2 Preserve the control-plane mental model

Users should think in terms of:

- workspaces
- catalogs and schemas
- compute resources
- jobs
- pipelines
- runs
- lineage
- system tables

Not just "run some Spark scripts."

### 4.3 Local-first, cloud-shaped

The platform should run on a developer laptop via Docker Compose first, while keeping an architecture that could later deploy to Kubernetes.

### 4.4 Use open standards where possible

Prefer:

- Delta Lake
- Apache Spark
- Structured Streaming
- open catalog APIs
- object storage abstractions

### 4.5 Build staged fidelity

We should build:

1. a strong practice platform first
2. a higher-fidelity Databricks-like UX next
3. advanced enterprise behaviors later

## 5. Proposed Platform: `LakeForge`

## 5.1 Product Goal

`LakeForge` is a local/open Data Engineering platform with a Databricks-like UX and operating model.

It provides:

- a workspace UI
- notebook and SQL authoring
- Spark-backed compute
- Delta-based tables on object storage
- governed metadata
- job orchestration
- declarative pipelines
- ingestion services
- lineage and observability

## 5.2 User Personas

### Platform learner

Wants to practice bronze/silver/gold pipelines, Delta operations, streaming, job orchestration, debugging, and governance.

### Interview prep engineer

Wants to demonstrate Databricks-flavored engineering skills with realistic artifacts:

- pipeline code
- job definitions
- quality checks
- data models
- operational dashboards

### Advanced builder

Wants to extend the platform with new task types, connectors, policies, and UI modules.

## 6. High-Level Architecture

```text
+------------------------------ LakeForge UI ------------------------------+
| Workspace | Notebooks | SQL Editor | Catalog | Jobs | Pipelines | Lineage |
+-----------------------------------+-------------------------------------+
                                    |
                                    v
+----------------------------- Control Plane API --------------------------+
| Auth | Workspace API | Catalog API | Jobs API | Pipelines API | Runs API |
| Lineage API | Query API | Bundle Deploy API | System Tables API          |
+-------------------+-------------------+-------------------+--------------+
                    |                   |                   |
                    v                   v                   v
          +----------------+   +-----------------+   +------------------+
          | Metadata DB    |   | Orchestration   |   | Event Bus        |
          | Postgres       |   | Temporal/Celery |   | Kafka/Redpanda   |
          +----------------+   +-----------------+   +------------------+
                    |                   |                   |
                    +---------+---------+-------------------+
                              |
                              v
+------------------------------- Compute Plane ----------------------------+
| Interactive Spark Sessions | Job Spark Runners | SQL Query Service      |
| Notebook kernel gateway    | Pipeline workers  | Streaming workers      |
+-----------------------------------+-------------------------------------+
                                    |
                                    v
+------------------------------ Data Plane --------------------------------+
| MinIO / S3-compatible object storage                                     |
| Delta tables | checkpoints | raw landing | managed tables | volumes      |
+-----------------------------------+-------------------------------------+
                                    |
                                    v
+---------------------------- Observability Plane -------------------------+
| system tables | lineage store | run logs | metrics | query history       |
+-------------------------------------------------------------------------+
```

## 7. Component Choices

These choices aim for maximum Databricks-like learning value with reasonable implementation cost.

## 7.1 Storage layer

### Choice

- MinIO for local S3-compatible object storage
- directory layout that mirrors cloud object storage patterns

### Why

- preserves object-storage mental model used by Databricks
- easy to run locally
- supports bronze landing zones, checkpoints, table paths, and managed storage

## 7.2 Table format

### Choice

- Delta Lake as the default table format

### Why

This is the single most important fidelity decision. Databricks DE practice without Delta is not close enough.

Required behaviors:

- ACID writes
- MERGE / UPSERT patterns
- schema evolution
- time travel
- streaming source and sink support
- table history

## 7.3 Processing engine

### Choice

- Apache Spark as the core execution engine
- Structured Streaming for streaming and incremental ingestion

### Why

This preserves the actual programming model used in Databricks DE interviews and production.

## 7.4 Metadata and governance layer

### Choice

- LakeForge Catalog Service with Unity-Catalog-like concepts
- optional adapter for open source Unity Catalog later
- metadata persisted in Postgres

### Why

Using a UC-like domain model is essential:

- metastore/workspace separation
- catalogs
- schemas
- tables
- views
- volumes
- grants
- tags
- lineage links

For implementation, a custom service is more practical than chasing full Unity Catalog parity on day one. But the API and object model should intentionally resemble Unity Catalog.

## 7.5 Notebook experience

### Choice

- JupyterLab-compatible backend execution
- custom Databricks-like notebook UI shell
- Python and SQL first in v1

### Why

Python + SQL covers the majority of DE workflows and keeps build scope sane.

Databricks-like notebook behaviors to emulate:

- cell-based execution
- attached compute selection
- mixed markdown/code workflow
- result tables and charts
- notebook run history

## 7.6 SQL analytics layer

### Choice

- SQL query service backed by Spark SQL sessions in v1
- warehouse abstraction in UI and API
- optional Trino/SQL acceleration later

### Why

The user needs the SQL warehouse experience conceptually, but we do not need to reproduce Databricks SQL internals to get strong DE training value.

## 7.7 Workflow orchestration

### Choice

- Temporal preferred for DAG/task orchestration
- fallback option: Celery + scheduler if we optimize for simplicity

### Why

Databricks Jobs supports retries, dependencies, scheduling, and multi-task workflows. Temporal maps well to durable workflow execution and run history.

Task types we should support:

- notebook task
- Python script task
- SQL task
- pipeline task
- shell task

## 7.8 Declarative pipelines

### Choice

- LakeForge Pipelines DSL with Databricks-inspired objects:
  - streaming tables
  - materialized views
  - expectations
  - flow graph

### Why

This is where Databricks DE differs from "just Spark." We need a higher-level pipeline abstraction, not only ad hoc jobs.

Implementation note:

- v1 pipeline spec stored as YAML + SQL/Python assets
- v2 adds Python decorators and SQL DDL closer to Databricks syntax

## 7.9 Version-controlled projects

### Choice

- Git-backed workspace projects
- bundle-like deployment descriptors

### Why

Databricks Git folders and Declarative Automation Bundles are important for modern DE engineering workflows and CI/CD practice.

## 8. Product Surface Area

## 8.1 Workspace

The workspace is the top-level user environment.

Objects:

- users
- groups
- folders
- notebooks
- files
- projects
- compute resources
- saved queries
- dashboards later

## 8.2 Catalog Explorer

The catalog experience should support:

- browse catalogs, schemas, tables, views, volumes
- table schema inspection
- table properties
- table history
- sample data preview
- ownership and grants
- upstream/downstream lineage
- freshness and quality signals

## 8.3 Compute

We should expose three Databricks-like compute abstractions.

### Interactive compute

For notebooks and ad hoc exploration.

Modes:

- shared interactive
- single-user interactive

### Job compute

Ephemeral compute spun up for workflow tasks.

Modes:

- serverless-like ephemeral runners
- configurable classic runners

### SQL warehouse

Pooled query execution for SQL editor and BI-style access.

Each compute resource should have:

- name
- type
- runtime version
- autoscale settings
- worker profile
- tags
- access policy
- state

## 8.4 Notebook UI

Notebook capabilities:

- Python and SQL cells
- markdown cells
- compute attachment picker
- run cell / run all
- inline table rendering
- chart rendering
- notebook parameters
- notebook scheduled runs through Jobs

Stretch:

- `%sql` magics
- notebook widgets
- side-by-side revision compare

## 8.5 SQL Editor

Capabilities:

- choose SQL warehouse
- write ANSI-style SQL against Delta tables
- save queries
- view query history
- inspect query profile
- export results

## 8.6 Jobs

Databricks-like job concepts to support:

- job definition
- DAG of tasks
- task dependencies
- task retries
- schedule or manual trigger
- run history
- task logs
- parameters
- notifications later

### Job schema

Core fields:

- `job_id`
- `name`
- `tags`
- `schedule`
- `max_concurrent_runs`
- `tasks[]`

Each task:

- `task_key`
- `task_type`
- `depends_on[]`
- `compute_ref`
- `source_ref`
- `parameters`
- `retry_policy`
- `timeout_seconds`

## 8.7 Pipelines

This is the closest analog to Lakeflow Spark Declarative Pipelines.

Pipeline features:

- declarative dataset graph
- batch or streaming mode
- streaming tables
- materialized views
- managed checkpoints
- expectations
- schema evolution controls
- run/update history
- event log

### Pipeline DSL v1

Each pipeline contains:

- pipeline metadata
- target catalog/schema
- source declarations
- dataset declarations
- quality expectations
- refresh mode
- compute profile

Example conceptual object model:

```yaml
pipeline:
  name: retail_medallion
  target: analytics.retail
  mode: continuous
  datasets:
    - name: bronze_orders
      kind: streaming_table
      source:
        type: autoloader
        path: s3://raw/retail/orders/
        format: json
    - name: silver_orders
      kind: streaming_table
      query: sql/silver_orders.sql
      expectations:
        - name: valid_order_id
          constraint: order_id IS NOT NULL
          action: fail
    - name: gold_daily_sales
      kind: materialized_view
      query: sql/gold_daily_sales.sql
```

## 8.8 Ingestion

We need an Auto Loader analog because this is central to Databricks DE practice.

### Ingestion modes

- file-drop incremental ingestion from object storage
- optional Kafka topic ingestion
- one-time backfill
- streaming continuous ingest

### Auto Loader analog

Service name: `CloudFiles Runner`

Responsibilities:

- detect new files in landing paths
- infer/evolve schema
- maintain checkpoint state
- invoke Spark Structured Streaming jobs
- land raw data into bronze Delta tables

User-facing options:

- source path
- file format
- schema mode
- rescued data column
- checkpoint path
- trigger mode

## 8.9 Delta table operations

The platform must make these operations easy to practice:

- create table
- append
- overwrite
- merge
- delete
- optimize later
- vacuum later
- describe history
- query older versions

## 8.10 Data quality

Databricks expectations are important enough to model directly.

Each expectation should support:

- name
- SQL boolean constraint
- action on violation

Actions:

- `warn`
- `drop`
- `fail`

The platform should capture:

- valid row count
- invalid row count
- dropped row count
- expectation failure reason
- dataset-level quality summary

## 8.11 Lineage

Lineage should be treated as a core platform feature, not an afterthought.

We need:

- table-to-table lineage
- column-level lineage where feasible
- job-to-table lineage
- notebook-to-table lineage
- pipeline-to-dataset lineage

### Capture strategy

- parse SQL logical plans when possible
- capture Spark read/write events
- annotate runs with source and target objects
- persist lineage edges in metadata store

## 8.12 System tables

This is a high-value Databricks-like feature for practice.

Expose a reserved `system` catalog with tables such as:

- `system.jobs.job_runs`
- `system.jobs.task_runs`
- `system.compute.resources`
- `system.query.history`
- `system.lineage.table_lineage`
- `system.billing.usage` later
- `system.pipelines.events`

This teaches users to analyze platform operations with SQL, just like in Databricks.

## 9. Object Model

## 9.1 Namespace hierarchy

```text
workspace
  -> metastore
    -> catalog
      -> schema
        -> table | view | volume | function
```

## 9.2 Core entities

- `User`
- `Group`
- `Workspace`
- `Metastore`
- `Catalog`
- `Schema`
- `Table`
- `View`
- `Volume`
- `ComputeResource`
- `Notebook`
- `Query`
- `Job`
- `JobRun`
- `TaskRun`
- `Pipeline`
- `PipelineRun`
- `LineageEdge`
- `ExpectationResult`
- `SystemEvent`

## 9.3 Table metadata

Each table should track:

- fully qualified name
- storage location
- format
- owner
- schema
- properties
- tags
- created/updated timestamps
- latest version
- history entries
- upstream lineage
- downstream lineage

## 10. Security and Governance Model

We do not need full enterprise cloud IAM in v1, but we do need the right concepts.

### Grants model

Support grants at:

- catalog
- schema
- table
- view
- volume
- compute resource

Privileges:

- `USE_CATALOG`
- `USE_SCHEMA`
- `SELECT`
- `MODIFY`
- `CREATE_TABLE`
- `CREATE_VIEW`
- `MANAGE`
- `ATTACH_COMPUTE`

### Ownership

Every major object has:

- owner user or group
- grants
- audit trail

## 11. Developer Workflow

## 11.1 Interactive workflow

1. Create or open a notebook.
2. Attach interactive compute.
3. Read raw data from landing zone or Delta tables.
4. Build bronze, silver, and gold tables.
5. Inspect results in Catalog Explorer.
6. Review lineage and table history.

## 11.2 Production workflow

1. Create a Git-backed project.
2. Write notebooks, SQL, and Python assets.
3. Define jobs and pipelines in config files.
4. Validate bundle/project config.
5. Deploy to workspace.
6. Schedule runs.
7. Monitor runs and system tables.

## 11.3 Streaming workflow

1. Land files into raw object storage.
2. Configure CloudFiles Runner.
3. Build streaming bronze tables.
4. Transform into silver streaming tables.
5. Materialize gold outputs.
6. Inspect checkpoints, run state, and expectations.

## 12. API Surface

The platform should be API-first.

### Core APIs

- `POST /api/workspaces`
- `GET /api/catalogs`
- `GET /api/catalogs/{catalog}/schemas/{schema}/tables`
- `POST /api/compute`
- `POST /api/notebooks/{id}/execute`
- `POST /api/sql/query`
- `POST /api/jobs`
- `POST /api/jobs/{id}/run`
- `GET /api/runs/{id}`
- `POST /api/pipelines`
- `POST /api/pipelines/{id}/update`
- `GET /api/lineage/table/{fqn}`
- `GET /api/system/query-history`

## 13. UI Modules

## 13.1 Required in v1

- sign-in
- workspace home
- notebook editor
- SQL editor
- catalog explorer
- jobs list + job detail + run detail
- pipelines list + pipeline detail + update history
- compute list
- lineage viewer
- system tables explorer

## 13.2 Nice to have later

- dashboards
- alerts
- assistant/chat panel
- query profile visualization
- schema compare UI

## 14. Data Layout Strategy

Use object storage paths that teach good lakehouse organization.

```text
s3://lakeforge/
  raw/
    retail/orders/
  managed/
    catalog=analytics/schema=retail/table=bronze_orders/
    catalog=analytics/schema=retail/table=silver_orders/
    catalog=analytics/schema=retail/table=gold_daily_sales/
  checkpoints/
    pipelines/retail_medallion/
  volumes/
    catalog=analytics/schema=ops/volume=shared_files/
```

## 15. Recommended Technical Stack

## 15.1 Frontend

- Next.js
- TypeScript
- Tailwind CSS
- Monaco editor
- React Query

## 15.2 Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Postgres
- Redis

## 15.3 Execution and orchestration

- Apache Spark
- Structured Streaming
- Temporal preferred
- Celery fallback

## 15.4 Storage and events

- MinIO
- Kafka or Redpanda

## 15.5 Auth

- local auth in v1
- OIDC later

## 15.6 Packaging and deployment

- Docker Compose for local development
- Kubernetes later

## 16. MVP Scope

This is the smallest version that still delivers strong Databricks-like practice value.

### MVP features

- local workspace UI
- notebook execution for Python + SQL
- Delta Lake tables on MinIO
- catalog/schema/table explorer
- Spark interactive compute
- Jobs with notebook/Python/SQL tasks
- pipeline definitions with streaming table/materialized view concepts
- file-based incremental ingestion
- expectations with warn/drop/fail
- table lineage
- system tables for jobs, queries, pipelines, compute
- Git-backed project folder

### Explicit MVP exclusions

- full multi-user collaboration
- Scala/R notebooks
- full UC interoperability
- enterprise IAM/network controls
- BI dashboards
- predictive optimization
- proprietary Databricks acceleration features

## 17. Implementation Roadmap

## Phase 1: Core lakehouse

- boot object storage and metadata DB
- run Spark with Delta support
- implement catalog/schema/table metadata APIs
- support table create/read/write/history

## Phase 2: Workspace and notebooks

- build workspace shell UI
- build notebook editor
- attach notebook to interactive Spark compute
- render tabular results

## Phase 3: Jobs and runs

- implement job/task model
- add scheduler and durable run history
- ship logs and task state transitions

## Phase 4: Pipelines and ingestion

- implement pipeline DSL
- add CloudFiles Runner
- add expectations
- add bronze/silver/gold sample projects

## Phase 5: Governance and lineage

- RBAC grants
- ownership
- lineage extraction
- Catalog Explorer lineage view

## Phase 6: SQL warehouse and system tables

- warehouse abstraction
- query history
- system catalog
- run analytics pages

## Phase 7: Bundles and Git workflow

- project deploy spec
- local validation
- environment targets

## 18. Interview-Practice Scenarios This Platform Should Support

- ingest JSON/CSV files incrementally into bronze
- build SCD Type 1 and Type 2 silver tables with MERGE
- create gold marts for reporting
- run continuous streaming pipelines
- add expectations and debug bad records
- examine table history and time travel
- diagnose failed job runs
- query system tables to inspect operational issues
- trace lineage from dashboard table back to raw source
- promote project changes through dev and prod-style targets

## 19. Important Fidelity Tradeoffs

Where this platform will be close to Databricks:

- Spark + Delta mental model
- medallion workflow
- governed namespaces
- job orchestration
- declarative pipeline concepts
- ingestion and quality patterns
- lineage and observability

Where it will not truly match Databricks:

- proprietary runtime optimizations
- enterprise cloud control plane depth
- full serverless economics and isolation model
- exact UI behavior and internal APIs

That is acceptable. For DE interview and skill-prep purposes, what matters most is workflow fidelity, not vendor-internal implementation fidelity.

## 20. Recommended Build Strategy

We should build this as a product platform, not as a pile of notebooks and scripts.

Recommended sequence:

1. control plane + metadata model
2. Spark/Delta data plane
3. notebooks + SQL editor
4. jobs
5. pipelines + ingestion
6. lineage + system tables
7. bundles/Git flow

This ordering gives us a usable platform early while preserving a path to higher Databricks resemblance.

## 21. Recommendation

The best design choice is:

- Delta Lake + Spark as the non-negotiable core
- MinIO as local object storage
- Postgres-backed UC-like metadata service
- FastAPI control plane
- Next.js UI
- Temporal-backed jobs/pipelines orchestration
- notebook + SQL interfaces as the primary user surface

That gives us the strongest ratio of:

- Databricks realism
- DE practice value
- implementation feasibility

## 22. Sources Reviewed

Primary Databricks sources reviewed on April 23, 2026:

- Databricks introduction, updated March 16, 2026: https://docs.databricks.com/aws/en/introduction
- Delta Lake in Databricks, updated March 31, 2026: https://docs.databricks.com/aws/en/delta/
- Unity Catalog overview, updated April 2, 2026: https://docs.databricks.com/aws/en/data-governance/unity-catalog
- Lakeflow Jobs, updated April 7, 2026: https://docs.databricks.com/aws/en/jobs
- Lakeflow Spark Declarative Pipelines concepts, updated March 4, 2026: https://docs.databricks.com/aws/en/ldp/concepts
- Auto Loader, updated April 14, 2026: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader
- Unity Catalog lineage, updated April 22, 2026: https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-lineage
- Compute overview, updated April 7, 2026: https://docs.databricks.com/aws/en/compute
- Serverless compute overview, updated March 19, 2026: https://docs.databricks.com/aws/en/compute/serverless
- Serverless jobs, updated April 15, 2026: https://docs.databricks.com/aws/en/jobs/run-serverless-jobs
- SQL warehouses, updated January 8, 2026: https://docs.databricks.com/aws/en/compute/sql-warehouse
- Databricks notebooks: https://docs.databricks.com/aws/en/notebooks
- Databricks Git folders, updated March 11, 2026: https://docs.databricks.com/aws/en/repos/
- Declarative Automation Bundles, updated March 16, 2026: https://docs.databricks.com/aws/en/dev-tools/bundles/
- Medallion architecture, updated October 3, 2025: https://docs.databricks.com/aws/en/lakehouse/medallion
- Unity Catalog table types, updated January 14, 2026: https://docs.databricks.com/aws/en/tables/delta-table
- System tables reference, updated April 16, 2026: https://docs.databricks.com/aws/en/admin/system-tables
- Pipeline expectations, updated February 4, 2026: https://docs.databricks.com/aws/en/ldp/expectations

Supporting open-source sources reviewed:

- Delta Lake docs, updated February 20, 2026: https://docs.delta.io/
- Spark Structured Streaming: https://spark.apache.org/streaming/
- Unity Catalog open source docs: https://docs.unitycatalog.io/
