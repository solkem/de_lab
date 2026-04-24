from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.notebook import NotebookRead
from app.schemas.lineage import LineageEdgeRead


class PipelineExpectation(BaseModel):
    name: str = Field(..., min_length=1)
    constraint_sql: str = Field(..., min_length=1)
    action: str = "WARN"


class PipelineExpectationResultRead(BaseModel):
    id: int
    pipeline_run_id: int
    expectation_name: str
    constraint_sql: str
    action: str
    status: str
    detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PipelineCreate(BaseModel):
    name: str = Field(..., min_length=1)
    notebook_id: int
    compute_resource_name: str = "starter-interactive"
    language: str = "PYTHON"
    code: str = Field(..., min_length=1)
    target_catalog: str = Field(..., min_length=1)
    target_schema: str = Field(..., min_length=1)
    target_table: str = Field(..., min_length=1)
    mode: str = "BATCH"
    expectations: list[PipelineExpectation] = []
    owner: str = "platform"


class PipelineRead(BaseModel):
    id: int
    name: str
    notebook_id: int
    compute_resource_name: str
    language: str
    code: str
    target_catalog: str
    target_schema: str
    target_table: str
    mode: str
    expectations_json: str | None
    owner: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PipelineRunRead(BaseModel):
    id: int
    pipeline_id: int
    status: str
    output_json: str | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PipelineDetail(BaseModel):
    pipeline: PipelineRead
    notebook: NotebookRead
    runs: list[PipelineRunRead]


class PipelineRunDetail(BaseModel):
    run: PipelineRunRead
    expectation_results: list[PipelineExpectationResultRead]
    lineage_edges: list[LineageEdgeRead]
