from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import IndexRun
from app.services.index_service import index_files

from app.core.config import settings


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)



@router.post("/index")
def run_index(
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = index_files(
            db=db,
            root_path=settings.index_root_path,
        )

        return {
            "status": result.status,
            "index_run_id": result.id,
            "scanned_files": result.scanned_files,
            "new_files": result.new_files,
            "updated_files": result.updated_files,
            "inactive_files": result.inactive_files,
            "skipped_files": result.skipped_files,
            "error_count": result.error_count,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except NotADirectoryError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="인덱싱 중 데이터베이스 오류가 발생했습니다.",
        ) from error

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"인덱싱 중 오류가 발생했습니다: {error}",
        ) from error


@router.get("/index/status")
def get_index_status(
    db: Session = Depends(get_db),
) -> dict:

    latest_run = db.scalar(
        select(IndexRun)
        .order_by(IndexRun.id.desc())
        .limit(1)
    )

    if latest_run is None:
        return {
            "status": "never_run",
            "message": "아직 인덱싱 실행 기록이 없습니다.",
        }

    return {
        "index_run_id": latest_run.id,
        "status": latest_run.status,
        "started_at": latest_run.started_at,
        "completed_at": latest_run.completed_at,
        "scanned_files": latest_run.scanned_files,
        "new_files": latest_run.new_files,
        "updated_files": latest_run.updated_files,
        "inactive_files": latest_run.inactive_files,
        "skipped_files": latest_run.skipped_files,
        "error_count": latest_run.error_count,
        "error_message": latest_run.error_message,
    }