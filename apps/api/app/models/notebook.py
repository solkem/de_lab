from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Notebook(Base):
    __tablename__ = "notebooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    path: Mapped[str] = mapped_column(String(1024), unique=True, index=True)
    language: Mapped[str] = mapped_column(String(50), default="PYTHON")
    owner: Mapped[str] = mapped_column(String(255), default="platform")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    runs: Mapped[list["NotebookRun"]] = relationship(
        back_populates="notebook", cascade="all, delete-orphan"
    )


class NotebookRun(Base):
    __tablename__ = "notebook_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    notebook_id: Mapped[int] = mapped_column(ForeignKey("notebooks.id"))
    compute_resource_name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    output_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    notebook: Mapped["Notebook"] = relationship(back_populates="runs")

