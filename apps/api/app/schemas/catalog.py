from datetime import datetime

from pydantic import BaseModel


class SchemaRead(BaseModel):
    id: int
    name: str
    owner: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CatalogRead(BaseModel):
    id: int
    name: str
    owner: str
    created_at: datetime
    schemas: list[SchemaRead] = []

    model_config = {"from_attributes": True}

