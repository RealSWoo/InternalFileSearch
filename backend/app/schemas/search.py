from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SearchResultSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    file_name: str
    extension: str | None
    full_path: str
    folder_path: str
    file_size: int | None
    modified_at: datetime | None
    score: int


class SearchResponseSchema(BaseModel):
    query: str
    normalized_query: str

    keywords: list[str]
    extensions: list[str]

    year: int | None
    recent: bool

    file_type: str | None

    total: int

    page: int
    page_size: int
    total_pages: int

    count: int

    response_time_ms: int

    results: list[SearchResultSchema]