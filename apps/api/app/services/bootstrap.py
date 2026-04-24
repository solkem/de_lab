from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import Catalog, Schema
from app.models.compute import ComputeResource


def seed_default_catalogs(db: Session) -> None:
    existing = db.scalar(select(Catalog).where(Catalog.name == "main"))
    if existing:
        return

    main = Catalog(name="main", owner="platform")
    main.schemas.extend(
        [
            Schema(name="bronze", owner="platform"),
            Schema(name="silver", owner="platform"),
            Schema(name="gold", owner="platform"),
        ]
    )

    system = Catalog(name="system", owner="platform")
    system.schemas.extend(
        [
            Schema(name="jobs", owner="platform"),
            Schema(name="compute", owner="platform"),
            Schema(name="query", owner="platform"),
            Schema(name="lineage", owner="platform"),
        ]
    )

    db.add_all([main, system])
    db.commit()


def seed_default_compute(db: Session) -> None:
    existing = db.scalar(
        select(ComputeResource).where(ComputeResource.name == "starter-interactive")
    )
    if existing:
        return

    db.add(
        ComputeResource(
            name="starter-interactive",
            resource_type="INTERACTIVE",
            access_mode="SINGLE_USER",
            runtime_version="spark-3.5-delta",
            status="RUNNING",
            owner="platform",
            endpoint="spark://localhost:7077",
        )
    )
    db.commit()
