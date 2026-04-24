from datetime import datetime

from pydantic import BaseModel


class ComputeResourceRead(BaseModel):
    id: int
    name: str
    resource_type: str
    access_mode: str
    runtime_version: str
    status: str
    owner: str
    endpoint: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

