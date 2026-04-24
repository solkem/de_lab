from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.compute import ComputeResource


def list_compute_resources(db: Session) -> list[ComputeResource]:
    stmt = select(ComputeResource).order_by(ComputeResource.name)
    return list(db.scalars(stmt).all())

