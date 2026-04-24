from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.job import Job, JobRun


def list_jobs(db: Session) -> list[Job]:
    stmt = select(Job).order_by(Job.created_at.desc(), Job.id.desc())
    return list(db.scalars(stmt).all())


def get_job(db: Session, job_id: int) -> Job | None:
    stmt = select(Job).options(selectinload(Job.runs)).where(Job.id == job_id)
    return db.scalar(stmt)


def create_job_record(
    db: Session,
    name: str,
    notebook_id: int,
    compute_resource_name: str,
    language: str,
    code: str,
    owner: str,
) -> Job:
    job = Job(
        name=name,
        task_type="NOTEBOOK",
        notebook_id=notebook_id,
        compute_resource_name=compute_resource_name,
        language=language.upper(),
        code=code,
        owner=owner,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_job_runs(db: Session, job_id: int) -> list[JobRun]:
    stmt = (
        select(JobRun)
        .where(JobRun.job_id == job_id)
        .order_by(JobRun.created_at.desc(), JobRun.id.desc())
    )
    return list(db.scalars(stmt).all())


def create_job_run(db: Session, job_id: int) -> JobRun:
    job_run = JobRun(job_id=job_id, status="RUNNING")
    db.add(job_run)
    db.commit()
    db.refresh(job_run)
    return job_run


def persist_job_run_success(job_run: JobRun, output_json: str | None, db: Session) -> None:
    job_run.status = "SUCCEEDED"
    job_run.output_json = output_json
    job_run.error_message = None
    db.add(job_run)
    db.commit()
    db.refresh(job_run)


def persist_job_run_failure(job_run: JobRun, error_message: str, db: Session) -> None:
    job_run.status = "FAILED"
    job_run.output_json = None
    job_run.error_message = error_message
    db.add(job_run)
    db.commit()
    db.refresh(job_run)
