export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";


export type Notebook = {
  id: number;
  name: string;
  path: string;
  language: string;
  owner: string;
  created_at: string;
};

export type NotebookRun = {
  id: number;
  notebook_id: number;
  compute_resource_name: string;
  language: string;
  status: string;
  output_json: string | null;
  error_message: string | null;
  created_at: string;
};

export type NotebookDetail = {
  notebook: Notebook;
  runs: NotebookRun[];
};

export type Job = {
  id: number;
  name: string;
  task_type: string;
  notebook_id: number;
  compute_resource_name: string;
  language: string;
  code: string;
  owner: string;
  created_at: string;
};

export type JobRun = {
  id: number;
  job_id: number;
  status: string;
  output_json: string | null;
  error_message: string | null;
  created_at: string;
};

export type JobDetail = {
  job: Job;
  notebook: Notebook;
  runs: JobRun[];
};

export type Pipeline = {
  id: number;
  name: string;
  notebook_id: number;
  compute_resource_name: string;
  language: string;
  code: string;
  target_catalog: string;
  target_schema: string;
  target_table: string;
  mode: string;
  expectations_json: string | null;
  owner: string;
  created_at: string;
};

export type PipelineRun = {
  id: number;
  pipeline_id: number;
  status: string;
  output_json: string | null;
  error_message: string | null;
  created_at: string;
};

export type PipelineDetail = {
  pipeline: Pipeline;
  notebook: Notebook;
  runs: PipelineRun[];
};

export type PipelineExpectation = {
  name: string;
  constraint_sql: string;
  action: string;
};

export type PipelineExpectationResult = {
  id: number;
  pipeline_run_id: number;
  expectation_name: string;
  constraint_sql: string;
  action: string;
  status: string;
  detail: string | null;
  created_at: string;
};

export type LineageEdge = {
  id: number;
  pipeline_run_id: number | null;
  source_type: string;
  source_name: string;
  target_type: string;
  target_name: string;
  relation_type: string;
  created_at: string;
};

export type PipelineRunDetail = {
  run: PipelineRun;
  expectation_results: PipelineExpectationResult[];
  lineage_edges: LineageEdge[];
};


export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      // Keep the fallback message if the response body is not JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}
