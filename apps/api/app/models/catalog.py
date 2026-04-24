from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Catalog(Base):
    __tablename__ = "catalogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    owner: Mapped[str] = mapped_column(String(255), default="platform")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    schemas: Mapped[list["Schema"]] = relationship(
        back_populates="catalog", cascade="all, delete-orphan"
    )


class Schema(Base):
    __tablename__ = "schemas"
    __table_args__ = (UniqueConstraint("catalog_id", "name", name="uq_schema_catalog_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(255), default="platform")
    catalog_id: Mapped[int] = mapped_column(ForeignKey("catalogs.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    catalog: Mapped["Catalog"] = relationship(back_populates="schemas")
    tables: Mapped[list["Table"]] = relationship(
        back_populates="schema", cascade="all, delete-orphan"
    )


class Table(Base):
    __tablename__ = "tables"
    __table_args__ = (UniqueConstraint("schema_id", "name", name="uq_table_schema_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    table_type: Mapped[str] = mapped_column(String(50), default="MANAGED")
    data_source_format: Mapped[str] = mapped_column(String(50), default="DELTA")
    owner: Mapped[str] = mapped_column(String(255), default="platform")
    storage_location: Mapped[str] = mapped_column(String(1024))
    comment: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    schema_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    materialized: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    schema_id: Mapped[int] = mapped_column(ForeignKey("schemas.id"))
    schema: Mapped["Schema"] = relationship(back_populates="tables")

    @property
    def full_name(self) -> str:
        return f"{self.schema.catalog.name}.{self.schema.name}.{self.name}"
