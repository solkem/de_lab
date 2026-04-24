from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps import db_session
from app.core.config import settings
from app.models.catalog import Catalog, Schema, Table
from app.models.compute import ComputeResource
from app.schemas.catalog import CatalogRead
from app.schemas.compute import ComputeResourceRead
from app.schemas.job import JobCreate, JobDetail, JobRead, JobRunRead
from app.schemas.lineage import LineageEdgeRead
from app.schemas.notebook import (
    NotebookCreate,
    NotebookDetail,
    NotebookExecutionRequest,
    NotebookExecutionResult,
    NotebookRead,
)
from app.schemas.pipeline import (
    PipelineCreate,
    PipelineDetail,
    PipelineRead,
    PipelineRunDetail,
    PipelineRunRead,
)
from app.schemas.table import TableCreate, TableDetail, TableHistoryRead, TableRead
from app.services.catalog import get_schema_by_name, list_tables
from app.services.compute import list_compute_resources
from app.services.execution import execute_notebook_code
from app.services.governance import (
    create_lineage_edges,
    evaluate_expectations,
    get_lineage_edges,
    get_pipeline_expectation_results,
    serialize_expectations,
)
from app.services.job import (
    create_job_record,
    create_job_run,
    get_job,
    list_job_runs,
    list_jobs,
    persist_job_run_failure,
    persist_job_run_success,
)
from app.services.notebook import (
    create_notebook_record,
    get_notebook,
    list_notebook_runs,
    list_notebooks,
)
from app.services.pipeline import (
    create_pipeline_record,
    create_pipeline_run,
    get_pipeline,
    list_pipeline_runs,
    list_pipelines,
    persist_pipeline_run_failure,
    persist_pipeline_run_success,
    target_fqn,
)
from app.services.spark import spark_dependencies_available, spark_runtime_status
from app.services.storage import managed_table_location
from app.services.table_runtime import (
    describe_table,
    fetch_table_history,
    get_table_by_name,
    materialize_delta_table,
    serialize_columns,
)


router = APIRouter()


@router.get("/health")
def healthcheck(db: Session = Depends(db_session)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "service": settings.app_name}


@router.get("/runtime/spark")
def get_spark_runtime() -> dict[str, str | bool]:
    runtime = spark_runtime_status()
    return {
        "available": runtime.available,
        "app_name": runtime.app_name,
        "master": runtime.master,
        "warehouse_dir": runtime.warehouse_dir,
        "detail": runtime.detail,
    }


@router.get("/catalogs", response_model=list[CatalogRead])
def list_catalogs(db: Session = Depends(db_session)) -> list[Catalog]:
    stmt = select(Catalog).options(selectinload(Catalog.schemas)).order_by(Catalog.name)
    return list(db.scalars(stmt).unique().all())


@router.get("/compute", response_model=list[ComputeResourceRead])
def get_compute_resources(db: Session = Depends(db_session)) -> list[ComputeResourceRead]:
    return list_compute_resources(db)


@router.get("/lineage", response_model=list[LineageEdgeRead])
def get_lineage(db: Session = Depends(db_session)) -> list[LineageEdgeRead]:
    return get_lineage_edges(db)


@router.get("/pipelines", response_model=list[PipelineRead])
def get_pipelines(db: Session = Depends(db_session)) -> list[PipelineRead]:
    return list_pipelines(db)


@router.get("/pipelines/{pipeline_id}", response_model=PipelineDetail)
def get_pipeline_detail(pipeline_id: int, db: Session = Depends(db_session)) -> PipelineDetail:
    pipeline = get_pipeline(db, pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline was not found")
    notebook = get_notebook(db, pipeline.notebook_id)
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline notebook was not found")
    runs = list_pipeline_runs(db, pipeline_id)
    return PipelineDetail(pipeline=pipeline, notebook=notebook, runs=runs)


@router.get("/pipelines/{pipeline_id}/runs", response_model=list[PipelineRunRead])
def get_runs_for_pipeline(
    pipeline_id: int, db: Session = Depends(db_session)
) -> list[PipelineRunRead]:
    pipeline = get_pipeline(db, pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline was not found")
    return list_pipeline_runs(db, pipeline_id)


@router.get("/pipelines/runs/{pipeline_run_id}", response_model=PipelineRunDetail)
def get_pipeline_run_detail(
    pipeline_run_id: int, db: Session = Depends(db_session)
) -> PipelineRunDetail:
    pipeline_run = next(
        (
            run
            for pipeline in list_pipelines(db)
            for run in list_pipeline_runs(db, pipeline.id)
            if run.id == pipeline_run_id
        ),
        None,
    )
    if pipeline_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline run was not found")
    expectation_results = get_pipeline_expectation_results(db, pipeline_run_id)
    lineage_edges = get_lineage_edges(db, pipeline_run_id)
    return PipelineRunDetail(
        run=pipeline_run,
        expectation_results=expectation_results,
        lineage_edges=lineage_edges,
    )


@router.post("/pipelines", response_model=PipelineRead, status_code=status.HTTP_201_CREATED)
def create_pipeline(payload: PipelineCreate, db: Session = Depends(db_session)) -> PipelineRead:
    notebook = get_notebook(db, payload.notebook_id)
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook was not found")
    compute = db.scalar(
        select(ComputeResource).where(ComputeResource.name == payload.compute_resource_name)
    )
    if compute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compute resource {payload.compute_resource_name} was not found",
        )
    schema = get_schema_by_name(db, payload.target_catalog, payload.target_schema)
    if schema is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema {payload.target_catalog}.{payload.target_schema} was not found",
        )
    try:
        return create_pipeline_record(
            db,
            name=payload.name,
            notebook_id=payload.notebook_id,
            compute_resource_name=payload.compute_resource_name,
            language=payload.language,
            code=payload.code,
            target_catalog=payload.target_catalog,
            target_schema=payload.target_schema,
            target_table=payload.target_table,
            mode=payload.mode,
            expectations_json=serialize_expectations(payload.expectations),
            owner=payload.owner,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Pipeline {payload.name} already exists",
        ) from exc


@router.post(
    "/pipelines/{pipeline_id}/run",
    response_model=PipelineRunRead,
    status_code=status.HTTP_201_CREATED,
)
def run_pipeline(pipeline_id: int, db: Session = Depends(db_session)) -> PipelineRunRead:
    pipeline = get_pipeline(db, pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline was not found")

    pipeline_run = create_pipeline_run(db, pipeline_id)
    try:
        notebook_run = execute_notebook_code(
            db,
            notebook_id=pipeline.notebook_id,
            payload=NotebookExecutionRequest(
                language=pipeline.language,
                code=pipeline.code,
                compute_resource_name=pipeline.compute_resource_name,
            ),
        )
        evaluate_expectations(db, pipeline_run, pipeline.expectations_json, notebook_run.output_json)
        create_lineage_edges(
            db,
            pipeline_run_id=pipeline_run.id,
            notebook_path=get_notebook(db, pipeline.notebook_id).path if get_notebook(db, pipeline.notebook_id) else pipeline.name,
            pipeline_name=pipeline.name,
            target_fqn=target_fqn(pipeline),
        )
        persist_pipeline_run_success(pipeline_run, notebook_run.output_json, db)
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        persist_pipeline_run_failure(pipeline_run, detail, db)
        raise
    except Exception as exc:
        persist_pipeline_run_failure(pipeline_run, str(exc), db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return pipeline_run


@router.get("/jobs", response_model=list[JobRead])
def get_jobs(db: Session = Depends(db_session)) -> list[JobRead]:
    return list_jobs(db)


@router.get("/jobs/{job_id}", response_model=JobDetail)
def get_job_detail(job_id: int, db: Session = Depends(db_session)) -> JobDetail:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job was not found")
    notebook = get_notebook(db, job.notebook_id)
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job notebook was not found")
    runs = list_job_runs(db, job_id)
    return JobDetail(job=job, notebook=notebook, runs=runs)


@router.get("/jobs/{job_id}/runs", response_model=list[JobRunRead])
def get_runs_for_job(job_id: int, db: Session = Depends(db_session)) -> list[JobRunRead]:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job was not found")
    return list_job_runs(db, job_id)


@router.post("/jobs", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(db_session)) -> JobRead:
    notebook = get_notebook(db, payload.notebook_id)
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook was not found")
    compute = db.scalar(
        select(ComputeResource).where(ComputeResource.name == payload.compute_resource_name)
    )
    if compute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compute resource {payload.compute_resource_name} was not found",
        )
    try:
        return create_job_record(
            db,
            name=payload.name,
            notebook_id=payload.notebook_id,
            compute_resource_name=payload.compute_resource_name,
            language=payload.language,
            code=payload.code,
            owner=payload.owner,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job {payload.name} already exists",
        ) from exc


@router.post("/jobs/{job_id}/run", response_model=JobRunRead, status_code=status.HTTP_201_CREATED)
def run_job(job_id: int, db: Session = Depends(db_session)) -> JobRunRead:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job was not found")

    job_run = create_job_run(db, job_id)
    try:
        notebook_run = execute_notebook_code(
            db,
            notebook_id=job.notebook_id,
            payload=NotebookExecutionRequest(
                language=job.language,
                code=job.code,
                compute_resource_name=job.compute_resource_name,
            ),
        )
        persist_job_run_success(job_run, notebook_run.output_json, db)
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        persist_job_run_failure(job_run, detail, db)
        raise
    except Exception as exc:
        persist_job_run_failure(job_run, str(exc), db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return job_run


@router.get("/notebooks", response_model=list[NotebookRead])
def get_notebooks(db: Session = Depends(db_session)) -> list[NotebookRead]:
    return list_notebooks(db)


@router.get("/notebooks/{notebook_id}", response_model=NotebookDetail)
def get_notebook_detail(notebook_id: int, db: Session = Depends(db_session)) -> NotebookDetail:
    notebook = get_notebook(db, notebook_id)
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook was not found")
    runs = list_notebook_runs(db, notebook_id)
    return NotebookDetail(notebook=notebook, runs=runs)


@router.get("/notebooks/{notebook_id}/runs", response_model=list[NotebookExecutionResult])
def get_notebook_runs(
    notebook_id: int, db: Session = Depends(db_session)
) -> list[NotebookExecutionResult]:
    notebook = get_notebook(db, notebook_id)
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook was not found")
    return list_notebook_runs(db, notebook_id)


@router.post("/notebooks", response_model=NotebookRead, status_code=status.HTTP_201_CREATED)
def create_notebook(payload: NotebookCreate, db: Session = Depends(db_session)) -> NotebookRead:
    try:
        return create_notebook_record(
            db, name=payload.name, path=payload.path, language=payload.language, owner=payload.owner
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Notebook path {payload.path} already exists",
        ) from exc


@router.post(
    "/notebooks/{notebook_id}/execute",
    response_model=NotebookExecutionResult,
    status_code=status.HTTP_201_CREATED,
)
def execute_notebook_cell(
    notebook_id: int, payload: NotebookExecutionRequest, db: Session = Depends(db_session)
) -> NotebookExecutionResult:
    return execute_notebook_code(db, notebook_id, payload)


@router.get("/tables", response_model=list[TableRead])
def get_tables(db: Session = Depends(db_session)) -> list[Table]:
    return list_tables(db)


@router.get(
    "/tables/{catalog_name}/{schema_name}/{table_name}",
    response_model=TableDetail,
)
def get_table_detail(
    catalog_name: str, schema_name: str, table_name: str, db: Session = Depends(db_session)
) -> TableDetail:
    table = get_table_by_name(db, catalog_name, schema_name, table_name)
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table was not found")

    if not table.materialized or not spark_dependencies_available():
        return TableDetail(table=table, storage_exists=table.materialized, spark_managed=False)

    detail = describe_table(table.storage_location)
    return TableDetail(table=table, **detail)


@router.get(
    "/tables/{catalog_name}/{schema_name}/{table_name}/history",
    response_model=TableHistoryRead,
)
def get_table_history(
    catalog_name: str, schema_name: str, table_name: str, db: Session = Depends(db_session)
) -> TableHistoryRead:
    table = get_table_by_name(db, catalog_name, schema_name, table_name)
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table was not found")
    if not table.materialized:
        return TableHistoryRead(full_name=table.full_name, entries=[])
    if not spark_dependencies_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Spark runtime dependencies are not installed",
        )

    return TableHistoryRead(full_name=table.full_name, entries=fetch_table_history(table.storage_location))


@router.post("/tables", response_model=TableRead, status_code=status.HTTP_201_CREATED)
def create_table(payload: TableCreate, db: Session = Depends(db_session)) -> Table:
    schema = get_schema_by_name(db, payload.catalog_name, payload.schema_name)
    if schema is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema {payload.catalog_name}.{payload.schema_name} was not found",
        )

    table = Table(
        name=payload.table_name,
        table_type=payload.table_type,
        data_source_format=payload.data_source_format,
        owner=payload.owner,
        comment=payload.comment,
        schema_json=serialize_columns(payload.columns),
        materialized=False,
        storage_location=managed_table_location(
            settings.minio_bucket, payload.catalog_name, payload.schema_name, payload.table_name
        ),
        schema_id=schema.id,
    )
    db.add(table)
    try:
        materialize_delta_table(table.storage_location, payload.columns)
        table.materialized = True
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Table {payload.catalog_name}.{payload.schema_name}.{payload.table_name} already exists",
        ) from exc

    stmt = (
        select(Table)
        .options(joinedload(Table.schema).joinedload(Schema.catalog))
        .where(Table.id == table.id)
    )
    created = db.scalar(stmt)
    if created is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Table creation failed")
    return created
