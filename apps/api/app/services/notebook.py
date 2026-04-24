from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.notebook import Notebook, NotebookRun


def list_notebooks(db: Session) -> list[Notebook]:
    stmt = select(Notebook).order_by(Notebook.path)
    return list(db.scalars(stmt).all())


def get_notebook(db: Session, notebook_id: int) -> Notebook | None:
    stmt = (
        select(Notebook)
        .options(selectinload(Notebook.runs))
        .where(Notebook.id == notebook_id)
    )
    return db.scalar(stmt)


def list_notebook_runs(db: Session, notebook_id: int) -> list[NotebookRun]:
    stmt = (
        select(NotebookRun)
        .where(NotebookRun.notebook_id == notebook_id)
        .order_by(NotebookRun.created_at.desc(), NotebookRun.id.desc())
    )
    return list(db.scalars(stmt).all())


def create_notebook_record(
    db: Session, name: str, path: str, language: str, owner: str
) -> Notebook:
    notebook = Notebook(name=name, path=path, language=language.upper(), owner=owner)
    db.add(notebook)
    db.commit()
    db.refresh(notebook)
    return notebook


def create_notebook_run(
    db: Session,
    notebook_id: int,
    compute_resource_name: str,
    language: str,
    code: str,
) -> NotebookRun:
    run = NotebookRun(
        notebook_id=notebook_id,
        compute_resource_name=compute_resource_name,
        language=language.upper(),
        code=code,
        status="RUNNING",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
