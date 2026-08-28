from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.database.models import File, IndexRun


SUPPORTED_EXTENSIONS = {
    ".ppt",
    ".pptx",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
    ".hwp",
    ".hwpx",
    ".jpg",
    ".jpeg",
    ".png",
    ".zip",
}


# 진행상황을 몇 개 파일마다 출력할지
PROGRESS_INTERVAL = 500


def normalize_text(value: str) -> str:
    """
    파일명/폴더명 검색용 문자열 정규화.
    """
    normalized = value.lower()

    for separator in ("_", "-", "."):
        normalized = normalized.replace(
            separator,
            " ",
        )

    normalized = " ".join(
        normalized.split()
    )

    return normalized


def timestamp_to_datetime(
    timestamp: float,
) -> datetime:
    """
    파일 시스템 timestamp를
    UTC 기준 naive datetime으로 변환한다.
    """
    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc,
    ).replace(
        tzinfo=None
    )


def normalize_datetime(
    value: datetime | None,
) -> datetime | None:
    """
    datetime 비교를 위해 UTC naive datetime으로 통일한다.
    """
    if value is None:
        return None

    if value.tzinfo is not None:
        return value.astimezone(
            timezone.utc
        ).replace(
            tzinfo=None
        )

    return value


def datetimes_equal(
    first: datetime | None,
    second: datetime | None,
    tolerance_seconds: float = 0.001,
) -> bool:
    """
    파일 수정시간 비교.

    NAS / 파일시스템 / SQLite 사이에서 발생할 수 있는
    아주 작은 시간 정밀도 차이를 허용한다.
    """
    first_normalized = (
        normalize_datetime(first)
    )

    second_normalized = (
        normalize_datetime(second)
    )

    if (
        first_normalized is None
        or second_normalized is None
    ):
        return (
            first_normalized
            == second_normalized
        )

    difference = abs(
        (
            first_normalized
            - second_normalized
        ).total_seconds()
    )

    return (
        difference
        <= tolerance_seconds
    )


def is_supported_file(
    path: Path,
) -> bool:
    """
    지원 대상 확장자인지 확인한다.
    """
    return (
        path.suffix.lower()
        in SUPPORTED_EXTENSIONS
    )


def get_file_metadata(
    file_path: Path,
    root_path: Path,
) -> dict:
    """
    실제 파일에서 DB 저장용 메타데이터를 생성한다.
    """
    stat = file_path.stat()

    file_name = file_path.name
    folder_path = str(
        file_path.parent
    )

    return {
        "file_name":
            file_name,

        "file_name_normalized":
            normalize_text(
                file_name
            ),

        "extension":
            file_path
            .suffix
            .lower()
            .lstrip("."),

        "full_path":
            str(
                file_path.resolve()
            ),

        "folder_path":
            folder_path,

        "folder_path_normalized":
            normalize_text(
                folder_path
            ),

        "root_path":
            str(
                root_path.resolve()
            ),

        "file_size":
            stat.st_size,

        "created_at":
            timestamp_to_datetime(
                stat.st_ctime
            ),

        "modified_at":
            timestamp_to_datetime(
                stat.st_mtime
            ),
    }


def print_progress(
    index_run: IndexRun,
    started_perf: float,
) -> None:
    """
    인덱싱 진행상황을 터미널에 출력한다.
    """
    elapsed = (
        perf_counter()
        - started_perf
    )

    supported_files = (
        index_run.scanned_files
        - index_run.skipped_files
    )

    print(
        "[Indexing] "
        f"scanned={index_run.scanned_files:,} "
        f"supported={supported_files:,} "
        f"new={index_run.new_files:,} "
        f"updated={index_run.updated_files:,} "
        f"skipped={index_run.skipped_files:,} "
        f"errors={index_run.error_count:,} "
        f"elapsed={elapsed:.1f}s"
    )


def index_files(
    db: Session,
    root_path: str,
) -> IndexRun:
    """
    지정한 root_path를 재귀 탐색하고
    files 테이블을 갱신한다.

    처리 대상:
    - 신규 파일 등록
    - 수정 파일 갱신
    - 기존 비활성 파일 재활성화
    - 삭제/이동된 파일 비활성화
    - 인덱싱 실행 내역 기록
    """

    root = Path(
        root_path
    )

    if not root.exists():
        raise FileNotFoundError(
            f"검색 대상 폴더를 찾을 수 없습니다: "
            f"{root_path}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"검색 대상 경로가 폴더가 아닙니다: "
            f"{root_path}"
        )

    started_perf = perf_counter()

    print()
    print("[Indexing started]")
    print(f"Root path : {root}")
    print()

    index_run = IndexRun(
        status="running",
        started_at=utc_now(),
        scanned_files=0,
        new_files=0,
        updated_files=0,
        inactive_files=0,
        skipped_files=0,
        error_count=0,
        error_message=None,
    )

    db.add(
        index_run
    )

    db.commit()

    db.refresh(
        index_run
    )

    current_paths: set[str] = set()

    try:
        for file_path in root.rglob("*"):

            try:
                if not file_path.is_file():
                    continue

                index_run.scanned_files += 1

                if not is_supported_file(
                    file_path
                ):
                    index_run.skipped_files += 1

                    if (
                        index_run.scanned_files
                        % PROGRESS_INTERVAL
                        == 0
                    ):
                        print_progress(
                            index_run=index_run,
                            started_perf=started_perf,
                        )

                    continue

                metadata = get_file_metadata(
                    file_path=file_path,
                    root_path=root,
                )

                full_path = (
                    metadata[
                        "full_path"
                    ]
                )

                current_paths.add(
                    full_path
                )

                existing_file = db.scalar(
                    select(File).where(
                        File.full_path
                        == full_path
                    )
                )

                #
                # 신규 파일
                #
                if existing_file is None:

                    new_file = File(
                        **metadata,
                        indexed_at=utc_now(),
                        is_active=True,
                    )

                    db.add(
                        new_file
                    )

                    index_run.new_files += 1

                else:
                    changed = False

                    #
                    # 파일 크기 변경
                    #
                    if (
                        existing_file.file_size
                        != metadata["file_size"]
                    ):
                        changed = True

                    #
                    # 수정시간 변경
                    #
                    if not datetimes_equal(
                        existing_file.modified_at,
                        metadata["modified_at"],
                    ):
                        changed = True

                    #
                    # 파일명 변경
                    #
                    if (
                        existing_file.file_name
                        != metadata["file_name"]
                    ):
                        changed = True

                    #
                    # 폴더 변경
                    #
                    if (
                        existing_file.folder_path
                        != metadata["folder_path"]
                    ):
                        changed = True

                    #
                    # 실제 변경된 경우
                    #
                    if changed:

                        existing_file.file_name = (
                            metadata[
                                "file_name"
                            ]
                        )

                        existing_file.file_name_normalized = (
                            metadata[
                                "file_name_normalized"
                            ]
                        )

                        existing_file.extension = (
                            metadata[
                                "extension"
                            ]
                        )

                        existing_file.folder_path = (
                            metadata[
                                "folder_path"
                            ]
                        )

                        existing_file.folder_path_normalized = (
                            metadata[
                                "folder_path_normalized"
                            ]
                        )

                        existing_file.root_path = (
                            metadata[
                                "root_path"
                            ]
                        )

                        existing_file.file_size = (
                            metadata[
                                "file_size"
                            ]
                        )

                        existing_file.created_at = (
                            metadata[
                                "created_at"
                            ]
                        )

                        existing_file.modified_at = (
                            metadata[
                                "modified_at"
                            ]
                        )

                        index_run.updated_files += 1

                    #
                    # 비활성 파일 재활성화
                    #
                    if not existing_file.is_active:

                        existing_file.is_active = True

                        if not changed:
                            index_run.updated_files += 1

                    existing_file.indexed_at = (
                        utc_now()
                    )

                #
                # 진행률 출력
                #
                if (
                    index_run.scanned_files
                    % PROGRESS_INTERVAL
                    == 0
                ):
                    print_progress(
                        index_run=index_run,
                        started_perf=started_perf,
                    )

            except (
                PermissionError,
                OSError,
            ):
                index_run.skipped_files += 1
                index_run.error_count += 1

            except Exception:
                index_run.skipped_files += 1
                index_run.error_count += 1

        indexed_root = str(
            root.resolve()
        )

        active_files = db.scalars(
            select(File).where(
                File.root_path
                == indexed_root,
                File.is_active.is_(
                    True
                ),
            )
        ).all()

        #
        # 이번 스캔에서 발견되지 않은 파일 비활성 처리
        #
        for existing_file in active_files:

            if (
                existing_file.full_path
                not in current_paths
            ):
                existing_file.is_active = False

                existing_file.indexed_at = (
                    utc_now()
                )

                index_run.inactive_files += 1

        index_run.status = (
            "completed"
        )

        index_run.completed_at = (
            utc_now()
        )

        db.commit()

        db.refresh(
            index_run
        )

        elapsed = (
            perf_counter()
            - started_perf
        )

        supported_files = (
            index_run.scanned_files
            - index_run.skipped_files
        )

        print()
        print("[Indexing completed]")
        print(
            f"Scanned   : "
            f"{index_run.scanned_files:,}"
        )
        print(
            f"Supported : "
            f"{supported_files:,}"
        )
        print(
            f"New       : "
            f"{index_run.new_files:,}"
        )
        print(
            f"Updated   : "
            f"{index_run.updated_files:,}"
        )
        print(
            f"Inactive  : "
            f"{index_run.inactive_files:,}"
        )
        print(
            f"Skipped   : "
            f"{index_run.skipped_files:,}"
        )
        print(
            f"Errors    : "
            f"{index_run.error_count:,}"
        )
        print(
            f"Elapsed   : "
            f"{elapsed:.1f}s"
        )
        print()

        return index_run

    except Exception as error:

        db.rollback()

        failed_run = db.get(
            IndexRun,
            index_run.id,
        )

        if failed_run is not None:

            failed_run.status = (
                "failed"
            )

            failed_run.completed_at = (
                utc_now()
            )

            failed_run.error_count += 1

            failed_run.error_message = (
                str(error)
            )

            db.commit()

        elapsed = (
            perf_counter()
            - started_perf
        )

        print()
        print("[Indexing failed]")
        print(
            f"Elapsed : {elapsed:.1f}s"
        )
        print(
            f"Error   : {error}"
        )
        print()

        raise