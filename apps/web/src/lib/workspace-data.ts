export const workspaceSummary = {
  workspace: "Local Dev Workspace",
  compute: 1,
  jobs: 1,
  pipelines: 1,
  catalogs: 2,
  tables: 0,
  notebooks: 1,
};

export const starterCatalogs = [
  {
    name: "main",
    description: "Primary lakehouse catalog for bronze, silver, and gold practice datasets.",
  },
  {
    name: "system",
    description: "Reserved operational metadata catalog for jobs, query history, compute, and lineage.",
  },
];

export const starterCompute = [
  {
    name: "starter-interactive",
    type: "INTERACTIVE",
    runtime: "spark-3.5-delta",
    status: "RUNNING",
  },
];

export const starterNotebooks = [
  {
    name: "Retail Bronze Exploration",
    language: "PYTHON",
    path: "/Workspace/Starter/Retail Bronze Exploration",
  },
];

export const starterJobs = [
  {
    name: "starter-notebook-job",
    type: "NOTEBOOK",
    compute: "starter-interactive",
  },
];

export const starterPipelines = [
  {
    name: "starter-medallion-pipeline",
    mode: "BATCH",
    target: "main.silver.silver_orders",
  },
];
