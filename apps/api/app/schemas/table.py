from datetime import datetime

from pydantic import BaseModel, Field


class TableColumnDefinition(BaseModel):
    name: str = Field(..., min_length=1)
    data_type: str = Field(..., min_length=1)
    nullable: bool = True


class TableCreate(BaseModel):
    catalog_name: str = Field(..., min_length=1)
    schema_name: str = Field(..., min_length=1)
    table_name: str = Field(..., min_length=1)
    table_type: str = "MANAGED"
    data_source_format: str = "DELTA"
    owner: str = "platform"
    comment: str | None = None
    columns: list[TableColumnDefinition] = Field(..., min_length=1)


class TableRead(BaseModel):
    id: int
    name: str
    table_type: str
    data_source_format: str
    owner: str
    storage_location: str
    comment: str | None
    schema_json: str | None
    materialized: bool
    created_at: datetime
    full_name: str

    model_config = {"from_attributes": True}


class TableDetail(BaseModel):
    table: TableRead
    storage_exists: bool
    spark_managed: bool
    num_files: int | None = None
    size_in_bytes: int | None = None


class TableHistoryEntry(BaseModel):
    version: int | None = None
    timestamp: str | None = None
    operation: str | None = None
    operation_parameters: dict[str, str] = {}
    read_version: int | None = None
    is_blind_append: bool | None = None


class TableHistoryRead(BaseModel):
    full_name: str
    entries: list[TableHistoryEntry]
