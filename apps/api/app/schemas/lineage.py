from datetime import datetime

from pydantic import BaseModel


class LineageEdgeRead(BaseModel):
    id: int
    pipeline_run_id: int | None
    source_type: str
    source_name: str
    target_type: str
    target_name: str
    relation_type: str
    created_at: datetime

    model_config = {"from_attributes": True}

