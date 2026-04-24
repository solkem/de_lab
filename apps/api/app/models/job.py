from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    task_type: Mapped[str] = mapped_column(String(50), default="NOTEBOOK")
    notebook_id: Mapped[int] = mapped_column(ForeignKey("notebooks.id"))
    compute_resource_name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(50), default="PYTHON")
    code: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(String(255), default="platform")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    runs: Mapped[list["JobRun"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class JobRun(Base):
    __tablename__ = "job_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    output_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    job: Mapped["Job"] = relationship(back_populates="runs")

