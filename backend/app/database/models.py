from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    file_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_name_normalized: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )

    extension: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    full_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )

    folder_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    folder_path_normalized: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )

    root_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    indexed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )


class IndexRun(Base):
    __tablename__ = "index_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    scanned_files: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    new_files: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    updated_files: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    inactive_files: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    skipped_files: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


class SearchLog(Base):
    __tablename__ = "search_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    normalized_query: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


Index(
    "ix_files_active_modified",
    File.is_active,
    File.modified_at,
)