import contextlib
import io
import json
import re
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.models.catalog import Table
from app.services.spark import build_spark_session


def _table_sql_mapping(tables: Iterable[Table]) -> dict[str, str]:
    return {
        table.full_name: f"delta.`{table.storage_location}`"
        for table in tables
        if table.materialized
    }


def _rewrite_sql(code: str, tables: Iterable[Table]) -> str:
    rewritten = code
    for full_name, path_ref in sorted(_table_sql_mapping(tables).items(), key=lambda item: -len(item[0])):
        pattern = rf"(?<![\w`]){re.escape(full_name)}(?![\w`])"
        rewritten = re.sub(pattern, path_ref, rewritten)
    return rewritten


def _preview_rows(rows: list[dict], limit: int = 20) -> list[dict]:
    return rows[:limit]


def _dataframe_preview(df) -> dict:
    rows = [row.asDict(recursive=True) for row in df.limit(20).collect()]
    return {
        "type": "dataframe",
        "columns": list(df.columns),
        "row_count_preview": len(rows),
        "rows": _preview_rows(rows),
    }


def execute_sql_cell(code: str, tables: Iterable[Table]) -> dict:
    spark = build_spark_session()
    try:
        rewritten = _rewrite_sql(code, tables)
        df = spark.sql(rewritten)
        if df.isStreaming:
            return {"type": "streaming", "message": "Streaming DataFrame returned"}
        if df.columns:
            preview = _dataframe_preview(df)
            preview["rewritten_sql"] = rewritten
            return preview
        return {"type": "statement", "message": "SQL statement executed", "rewritten_sql": rewritten}
    finally:
        spark.stop()


def execute_python_cell(code: str, tables: Iterable[Table]) -> dict:
    spark = build_spark_session()
    stdout = io.StringIO()
    namespace = {
        "spark": spark,
        "tables": {table.full_name: table.storage_location for table in tables if table.materialized},
        "result": None,
    }
    try:
        with contextlib.redirect_stdout(stdout):
            exec(code, {"__builtins__": __builtins__}, namespace)

        result = namespace.get("result")
        output = stdout.getvalue().strip()

        if result is not None and hasattr(result, "collect") and hasattr(result, "columns"):
            preview = _dataframe_preview(result)
            preview["stdout"] = output
            return preview

        return {
            "type": "python",
            "stdout": output,
            "result_repr": None if result is None else repr(result),
        }
    finally:
        spark.stop()


def persist_run_success(run, output: dict, db: Session) -> None:
    run.status = "SUCCEEDED"
    run.output_json = json.dumps(output)
    run.error_message = None
    db.add(run)
    db.commit()
    db.refresh(run)


def persist_run_failure(run, error_message: str, db: Session) -> None:
    run.status = "FAILED"
    run.output_json = None
    run.error_message = error_message
    db.add(run)
    db.commit()
    db.refresh(run)
