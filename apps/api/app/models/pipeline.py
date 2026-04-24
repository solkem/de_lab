from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    notebook_id: Mapped[int] = mapped_column(ForeignKey("notebooks.id"))
    compute_resource_name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(50), default="PYTHON")
    code: Mapped[str] = mapped_column(Text)
    target_catalog: Mapped[str] = mapped_column(String(255))
    target_schema: Mapped[str] = mapped_column(String(255))
    target_table: Mapped[str] = mapped_column(String(255))
    mode: Mapped[str] = mapped_column(String(50), default="BATCH")
    expectations_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str] = mapped_column(String(255), default="platform")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    runs: Mapped[list["PipelineRun"]] = relationship(
        back_populates="pipeline", cascade="all, delete-orphan"
    )


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_id: Mapped[int] = mapped_column(ForeignKey("pipelines.id"))
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    output_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    pipeline: Mapped["Pipeline"] = relationship(back_populates="runs")


class PipelineExpectationResult(Base):
    __tablename__ = "pipeline_expectation_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_run_id: Mapped[int] = mapped_column(ForeignKey("pipeline_runs.id"))
    expectation_name: Mapped[str] = mapped_column(String(255))
    constraint_sql: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(String(50), default="WARN")
    status: Mapped[str] = mapped_column(String(50), default="UNKNOWN")
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class LineageEdge(Base):
    __tablename__ = "lineage_edges"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_run_id: Mapped[int | None] = mapped_column(ForeignKey("pipeline_runs.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50))
    source_name: Mapped[str] = mapped_column(String(512))
    target_type: Mapped[str] = mapped_column(String(50))
    target_name: Mapped[str] = mapped_column(String(512))
    relation_type: Mapped[str] = mapped_column(String(50), default="DERIVES")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
