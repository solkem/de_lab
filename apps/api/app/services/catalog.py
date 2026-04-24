from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.catalog import Catalog, Schema, Table


def get_catalog_by_name(db: Session, catalog_name: str) -> Catalog | None:
    stmt = select(Catalog).where(Catalog.name == catalog_name)
    return db.scalar(stmt)


def get_schema_by_name(db: Session, catalog_name: str, schema_name: str) -> Schema | None:
    stmt = (
        select(Schema)
        .join(Schema.catalog)
        .options(joinedload(Schema.catalog))
        .where(Catalog.name == catalog_name, Schema.name == schema_name)
    )
    return db.scalar(stmt)


def list_tables(db: Session) -> list[Table]:
    stmt = (
        select(Table)
        .options(joinedload(Table.schema).joinedload(Schema.catalog))
        .order_by(Table.name)
    )
    return list(db.scalars(stmt).unique().all())

