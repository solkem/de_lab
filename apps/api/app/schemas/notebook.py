from datetime import datetime

from pydantic import BaseModel, Field


class NotebookCreate(BaseModel):
    name: str = Field(..., min_length=1)
    path: str = Field(..., min_length=1)
    language: str = "PYTHON"
    owner: str = "platform"


class NotebookRead(BaseModel):
    id: int
    name: str
    path: str
    language: str
    owner: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NotebookExecutionRequest(BaseModel):
    language: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    compute_resource_name: str = "starter-interactive"


class NotebookExecutionResult(BaseModel):
    id: int
    notebook_id: int
    compute_resource_name: str
    language: str
    status: str
    output_json: str | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotebookDetail(BaseModel):
    notebook: NotebookRead
    runs: list[NotebookExecutionResult]
