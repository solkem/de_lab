from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.compute import ComputeResource
from app.models.notebook import NotebookRun
from app.schemas.notebook import NotebookExecutionRequest
from app.services.catalog import list_tables
from app.services.notebook import create_notebook_run, get_notebook
from app.services.notebook_runtime import (
    execute_python_cell,
    execute_sql_cell,
    persist_run_failure,
    persist_run_success,
)
from app.services.spark import spark_dependencies_available, spark_runtime_status


def execute_notebook_code(
    db: Session, notebook_id: int, payload: NotebookExecutionRequest
) -> NotebookRun:
    notebook = get_notebook(db, notebook_id)
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook was not found")
    if not spark_dependencies_available():
        runtime = spark_runtime_status()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=runtime.detail,
        )

    compute = db.scalar(
        select(ComputeResource).where(ComputeResource.name == payload.compute_resource_name)
    )
    if compute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compute resource {payload.compute_resource_name} was not found",
        )

    run = create_notebook_run(
        db,
        notebook_id=notebook.id,
        compute_resource_name=payload.compute_resource_name,
        language=payload.language,
        code=payload.code,
    )
    tables = list_tables(db)

    try:
        language = payload.language.upper()
        if language == "SQL":
            output = execute_sql_cell(payload.code, tables)
        elif language == "PYTHON":
            output = execute_python_cell(payload.code, tables)
        else:
            raise ValueError(f"Unsupported notebook language: {payload.language}")
        persist_run_success(run, output, db)
    except ValueError as exc:
        persist_run_failure(run, str(exc), db)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        persist_run_failure(run, str(exc), db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return run
