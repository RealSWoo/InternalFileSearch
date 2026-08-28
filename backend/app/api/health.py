from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import engine


router = APIRouter(
    prefix="/api",
    tags=["Health"],
)


@router.get("/health")
def health_check() -> dict:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
        }

    except SQLAlchemyError:
        return {
            "status": "error",
            "database": "disconnected",
        }