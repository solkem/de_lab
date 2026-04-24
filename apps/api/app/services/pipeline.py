from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.pipeline import Pipeline, PipelineExpectationResult, PipelineRun


def list_pipelines(db: Session) -> list[Pipeline]:
    stmt = select(Pipeline).order_by(Pipeline.created_at.desc(), Pipeline.id.desc())
    return list(db.scalars(stmt).all())


def get_pipeline(db: Session, pipeline_id: int) -> Pipeline | None:
    stmt = select(Pipeline).options(selectinload(Pipeline.runs)).where(Pipeline.id == pipeline_id)
    return db.scalar(stmt)


def create_pipeline_record(
    db: Session,
    name: str,
    notebook_id: int,
    compute_resource_name: str,
    language: str,
    code: str,
    target_catalog: str,
    target_schema: str,
    target_table: str,
    mode: str,
    expectations_json: str | None,
    owner: str,
) -> Pipeline:
    pipeline = Pipeline(
        name=name,
        notebook_id=notebook_id,
        compute_resource_name=compute_resource_name,
        language=language.upper(),
        code=code,
        target_catalog=target_catalog,
        target_schema=target_schema,
        target_table=target_table,
        mode=mode.upper(),
        expectations_json=expectations_json,
        owner=owner,
    )
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    return pipeline


def list_pipeline_runs(db: Session, pipeline_id: int) -> list[PipelineRun]:
    stmt = (
        select(PipelineRun)
        .where(PipelineRun.pipeline_id == pipeline_id)
        .order_by(PipelineRun.created_at.desc(), PipelineRun.id.desc())
    )
    return list(db.scalars(stmt).all())


def create_pipeline_run(db: Session, pipeline_id: int) -> PipelineRun:
    pipeline_run = PipelineRun(pipeline_id=pipeline_id, status="RUNNING")
    db.add(pipeline_run)
    db.commit()
    db.refresh(pipeline_run)
    return pipeline_run


def persist_pipeline_run_success(
    pipeline_run: PipelineRun, output_json: str | None, db: Session
) -> None:
    pipeline_run.status = "SUCCEEDED"
    pipeline_run.output_json = output_json
    pipeline_run.error_message = None
    db.add(pipeline_run)
    db.commit()
    db.refresh(pipeline_run)


def persist_pipeline_run_failure(
    pipeline_run: PipelineRun, error_message: str, db: Session
) -> None:
    pipeline_run.status = "FAILED"
    pipeline_run.output_json = None
    pipeline_run.error_message = error_message
    db.add(pipeline_run)
    db.commit()
    db.refresh(pipeline_run)


def target_fqn(pipeline: Pipeline) -> str:
    return f"{pipeline.target_catalog}.{pipeline.target_schema}.{pipeline.target_table}"
