from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.search import SearchResponseSchema
from app.services.search_service import search_files


router = APIRouter(
    prefix="/api/search",
    tags=["search"],
)


@router.get(
    "",
    response_model=SearchResponseSchema,
)
def search(
    q: str = Query(
        ...,
        min_length=1,
    ),
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        5,
        ge=1,
        le=100,
    ),
    file_type: str | None = Query(
        None,
    ),
    db: Session = Depends(
        get_db
    ),
) -> SearchResponseSchema:
    try:
        response = search_files(
            db=db,
            query=q,
            page=page,
            page_size=page_size,
            file_type=file_type,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return SearchResponseSchema(
        query=response.query,
        normalized_query=(
            response.normalized_query
        ),
        keywords=response.keywords,
        extensions=response.extensions,
        year=response.year,
        recent=response.recent,
        file_type=response.file_type,
        total=response.total,
        page=response.page,
        page_size=response.page_size,
        total_pages=response.total_pages,
        count=len(
            response.results
        ),
        response_time_ms=(
            response.response_time_ms
        ),
        results=response.results,
    )