import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.catalog import Schema, Table
from app.schemas.table import TableColumnDefinition
from app.services.spark import build_spark_session

try:
    from pyspark.sql.types import (
        BooleanType,
        DoubleType,
        IntegerType,
        LongType,
        StringType,
        StructField,
        StructType,
        TimestampType,
    )
except ImportError:  # pragma: no cover
    BooleanType = None
    DoubleType = None
    IntegerType = None
    LongType = None
    StringType = None
    StructField = None
    StructType = None
    TimestampType = None


SPARK_TYPE_MAP = {
    "string": StringType() if StringType else None,
    "integer": IntegerType() if IntegerType else None,
    "int": IntegerType() if IntegerType else None,
    "bigint": LongType() if LongType else None,
    "long": LongType() if LongType else None,
    "double": DoubleType() if DoubleType else None,
    "boolean": BooleanType() if BooleanType else None,
    "timestamp": TimestampType() if TimestampType else None,
}


def serialize_columns(columns: list[TableColumnDefinition]) -> str:
    return json.dumps([column.model_dump() for column in columns])


def deserialize_columns(schema_json: str | None) -> list[dict]:
    if not schema_json:
        return []
    return json.loads(schema_json)


def build_struct_type(columns: list[TableColumnDefinition]) -> Any:
    if StructType is None or StructField is None:
        raise RuntimeError("Spark SQL types are not installed")

    fields: list[Any] = []
    for column in columns:
        spark_type = SPARK_TYPE_MAP.get(column.data_type.lower())
        if spark_type is None:
            raise ValueError(f"Unsupported Spark data type: {column.data_type}")
        fields.append(StructField(column.name, spark_type, column.nullable))
    return StructType(fields)


def materialize_delta_table(storage_location: str, columns: list[TableColumnDefinition]) -> None:
    spark = build_spark_session()
    try:
        schema = build_struct_type(columns)
        spark.createDataFrame([], schema).write.format("delta").mode("errorifexists").save(
            storage_location
        )
    finally:
        spark.stop()


def describe_table(storage_location: str) -> dict:
    spark = build_spark_session()
    try:
        detail = spark.sql(f"DESCRIBE DETAIL delta.`{storage_location}`").collect()[0].asDict()
        return {
            "storage_exists": True,
            "spark_managed": True,
            "num_files": detail.get("numFiles"),
            "size_in_bytes": detail.get("sizeInBytes"),
        }
    finally:
        spark.stop()


def fetch_table_history(storage_location: str) -> list[dict]:
    spark = build_spark_session()
    try:
        rows = spark.sql(f"DESCRIBE HISTORY delta.`{storage_location}`").collect()
        entries: list[dict] = []
        for row in rows:
            entry = row.asDict()
            entries.append(
                {
                    "version": entry.get("version"),
                    "timestamp": str(entry.get("timestamp")) if entry.get("timestamp") else None,
                    "operation": entry.get("operation"),
                    "operation_parameters": entry.get("operationParameters") or {},
                    "read_version": entry.get("readVersion"),
                    "is_blind_append": entry.get("isBlindAppend"),
                }
            )
        return entries
    finally:
        spark.stop()


def get_table_by_name(
    db: Session, catalog_name: str, schema_name: str, table_name: str
) -> Table | None:
    stmt = (
        select(Table)
        .join(Table.schema)
        .join(Schema.catalog)
        .options(joinedload(Table.schema).joinedload(Schema.catalog))
        .where(
            Schema.name == schema_name,
            Table.name == table_name,
            Schema.catalog.has(name=catalog_name),
        )
    )
    return db.scalar(stmt)
