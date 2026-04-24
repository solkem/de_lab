from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.notebook import NotebookRead


class JobCreate(BaseModel):
    name: str = Field(..., min_length=1)
    notebook_id: int
    compute_resource_name: str = "starter-interactive"
    language: str = "PYTHON"
    code: str = Field(..., min_length=1)
    owner: str = "platform"


class JobRead(BaseModel):
    id: int
    name: str
    task_type: str
    notebook_id: int
    compute_resource_name: str
    language: str
    code: str
    owner: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobRunRead(BaseModel):
    id: int
    job_id: int
    status: str
    output_json: str | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobDetail(BaseModel):
    job: JobRead
    notebook: NotebookRead
    runs: list[JobRunRead]

