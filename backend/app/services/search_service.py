import math
import re

from dataclasses import dataclass
from difflib import SequenceMatcher
from time import perf_counter

from sqlalchemy import extract, or_, select
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.database.models import File, SearchLog
from app.services.query_parser import (
    ParsedQuery,
    parse_query,
)


GENERIC_DOCUMENT_KEYWORDS = {
    "제안서",
    "보고서",
    "계획서",
    "계약서",
    "견적서",
    "회의록",
    "자료",
    "문서",
    "최종",
}


FUZZY_MATCH_THRESHOLD = 0.72

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 5
MAX_PAGE_SIZE = 100

# DB에서 정밀 검색 대상으로 가져올
# 1차 후보군 최대 개수
CANDIDATE_LIMIT = 1000


FILE_TYPE_EXTENSIONS = {
    "pdf": {
        "pdf",
    },
    "excel": {
        "xls",
        "xlsx",
        "csv",
    },
    "ppt": {
        "ppt",
        "pptx",
    },
    "word": {
        "doc",
        "docx",
    },
}


@dataclass
class SearchResult:
    id: int
    file_name: str
    extension: str | None
    full_path: str
    folder_path: str
    file_size: int | None
    modified_at: object
    score: int


@dataclass
class SearchResponse:
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

    results: list[SearchResult]
    response_time_ms: int


def tokenize_search_text(
    value: str,
) -> list[str]:
    return [
        token
        for token in re.split(
            r"\s+",
            value,
        )
        if token
    ]


def similarity(
    first: str,
    second: str,
) -> float:
    return SequenceMatcher(
        None,
        first,
        second,
    ).ratio()


def keyword_match_type(
    keyword: str,
    target: str,
) -> str | None:
    if keyword in target:
        return "exact"

    target_tokens = tokenize_search_text(
        target
    )

    for token in target_tokens:
        if len(keyword) < 2:
            continue

        if (
            keyword in token
            or token in keyword
        ):
            return "partial"

    if len(keyword) < 2:
        return None

    for token in target_tokens:
        if len(token) < 2:
            continue

        match_score = similarity(
            keyword,
            token,
        )

        if (
            match_score
            >= FUZZY_MATCH_THRESHOLD
        ):
            return "fuzzy"

    return None


def matches_year(
    file: File,
    year: int,
) -> bool:
    """
    Python 정밀 검증용 연도 확인.

    DB 후보검색에서도 연도를 먼저 적용하지만,
    최종적으로 한 번 더 확인한다.
    """

    year_text = str(year)

    if (
        year_text
        in file.file_name_normalized
    ):
        return True

    if (
        year_text
        in file.folder_path_normalized
    ):
        return True

    if (
        file.modified_at
        and file.modified_at.year == year
    ):
        return True

    return False


def calculate_score(
    file: File,
    parsed_query: ParsedQuery,
) -> int:
    if not parsed_query.keywords:
        return 0

    file_name = (
        file.file_name_normalized
    )

    folder_path = (
        file.folder_path_normalized
    )

    combined = (
        f"{file_name} {folder_path}"
    )

    keywords = (
        parsed_query.keywords
    )

    normalized_query = (
        parsed_query.normalized_query
    )

    score = 0

    anchor_keywords = [
        keyword
        for keyword in keywords
        if keyword
        not in GENERIC_DOCUMENT_KEYWORDS
    ]

    if anchor_keywords:
        anchor_matched = False

        for keyword in anchor_keywords:
            match_type = keyword_match_type(
                keyword,
                combined,
            )

            if match_type is not None:
                anchor_matched = True
                break

        if not anchor_matched:
            return 0

    file_stem = file_name

    if file.extension:
        suffix = f" {file.extension}"

        if file_stem.endswith(suffix):
            file_stem = file_stem[
                : -len(suffix)
            ].strip()

    if file_stem == normalized_query:
        score += 200

    elif (
        normalized_query
        and normalized_query in file_name
    ):
        score += 100

    matched_keyword_count = 0

    for keyword in keywords:

        file_match = keyword_match_type(
            keyword,
            file_name,
        )

        folder_match = keyword_match_type(
            keyword,
            folder_path,
        )

        if file_match == "exact":
            score += 50
            matched_keyword_count += 1

        elif file_match == "partial":
            score += 35
            matched_keyword_count += 1

        elif file_match == "fuzzy":
            score += 20
            matched_keyword_count += 1

        elif folder_match == "exact":
            score += 25
            matched_keyword_count += 1

        elif folder_match == "partial":
            score += 15
            matched_keyword_count += 1

        elif folder_match == "fuzzy":
            score += 8
            matched_keyword_count += 1

    if (
        matched_keyword_count
        == len(keywords)
    ):
        score += 100

    for keyword in anchor_keywords:

        file_match = keyword_match_type(
            keyword,
            file_name,
        )

        folder_match = keyword_match_type(
            keyword,
            folder_path,
        )

        if file_match == "exact":
            score += 60

        elif file_match == "partial":
            score += 40

        elif file_match == "fuzzy":
            score += 20

        elif folder_match == "exact":
            score += 30

        elif folder_match == "partial":
            score += 20

        elif folder_match == "fuzzy":
            score += 10

    return score


def resolve_extension_filter(
    parsed_query: ParsedQuery,
    file_type: str | None,
) -> set[str]:
    extensions = set(
        parsed_query.extensions
    )

    if (
        file_type
        and file_type != "all"
    ):
        file_type_extensions = (
            FILE_TYPE_EXTENSIONS.get(
                file_type
            )
        )

        if file_type_extensions is None:
            raise ValueError(
                f"지원하지 않는 파일 유형입니다: {file_type}"
            )

        if extensions:
            extensions = (
                extensions
                & file_type_extensions
            )

        else:
            extensions = set(
                file_type_extensions
            )

    return extensions


def build_candidate_statement(
    parsed_query: ParsedQuery,
    extension_filter: set[str],
):
    """
    DB에서 1차 후보군을 추출한다.

    중요한 점:
    연도 검색은 CANDIDATE_LIMIT 적용 전에
    DB 단계에서 먼저 적용한다.
    """

    statement = select(File).where(
        File.is_active.is_(True)
    )

    #
    # 확장자 필터
    #
    if extension_filter:
        statement = statement.where(
            File.extension.in_(
                extension_filter
            )
        )

    #
    # 연도 필터
    #
    # 파일명 / 폴더명에 연도가 있거나
    # modified_at 연도가 일치하는 경우
    #
    if parsed_query.year is not None:
        year_text = str(
            parsed_query.year
        )

        year_pattern = (
            f"%{year_text}%"
        )

        statement = statement.where(
            or_(
                File.file_name_normalized.like(
                    year_pattern
                ),
                File.folder_path_normalized.like(
                    year_pattern
                ),
                extract(
                    "year",
                    File.modified_at,
                )
                == parsed_query.year,
            )
        )

    #
    # 키워드가 없는 경우
    #
    if not parsed_query.keywords:
        return (
            statement
            .order_by(
                File.modified_at.desc()
            )
            .limit(
                CANDIDATE_LIMIT
            )
        )

    conditions = []

    #
    # 검색 키워드 후보 추출
    #
    for keyword in parsed_query.keywords:

        like_pattern = (
            f"%{keyword}%"
        )

        conditions.append(
            File.file_name_normalized.like(
                like_pattern
            )
        )

        conditions.append(
            File.folder_path_normalized.like(
                like_pattern
            )
        )

    statement = statement.where(
        or_(*conditions)
    )

    #
    # 최근 파일부터 후보 확보
    #
    statement = statement.order_by(
        File.modified_at.desc()
    )

    #
    # 정밀 검색 후보군 상한
    #
    statement = statement.limit(
        CANDIDATE_LIMIT
    )

    return statement


def search_files(
    db: Session,
    query: str,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    file_type: str | None = None,
) -> SearchResponse:
    started_at = perf_counter()

    parsed_query = parse_query(
        query
    )

    if (
        not parsed_query.keywords
        and not parsed_query.extensions
    ):
        raise ValueError(
            "검색 가능한 키워드가 없습니다."
        )

    page = max(
        1,
        page,
    )

    page_size = max(
        1,
        min(
            page_size,
            MAX_PAGE_SIZE,
        ),
    )

    extension_filter = (
        resolve_extension_filter(
            parsed_query=parsed_query,
            file_type=file_type,
        )
    )

    #
    # 검색어 자체 확장자와
    # UI 확장자 필터가 충돌할 경우
    #
    # 예:
    # "스타필드 PDF" 검색 후 PPT 버튼 클릭
    #
    if (
        parsed_query.extensions
        and file_type
        and file_type != "all"
        and not extension_filter
    ):
        files = []

    else:
        statement = (
            build_candidate_statement(
                parsed_query=parsed_query,
                extension_filter=extension_filter,
            )
        )

        files = db.scalars(
            statement
        ).all()

    scored_results: list[
        SearchResult
    ] = []

    #
    # 후보군 정밀 평가
    #
    for file in files:

        #
        # DB에서도 연도 필터를 적용했지만
        # 최종적으로 한 번 더 검증
        #
        if (
            parsed_query.year
            is not None
            and not matches_year(
                file,
                parsed_query.year,
            )
        ):
            continue

        if not parsed_query.keywords:
            score = 1

        else:
            score = calculate_score(
                file=file,
                parsed_query=parsed_query,
            )

        if score <= 0:
            continue

        scored_results.append(
            SearchResult(
                id=file.id,
                file_name=file.file_name,
                extension=file.extension,
                full_path=file.full_path,
                folder_path=file.folder_path,
                file_size=file.file_size,
                modified_at=file.modified_at,
                score=score,
            )
        )

    #
    # 최근/최신 검색
    #
    if parsed_query.recent:

        scored_results.sort(
            key=lambda result: (
                (
                    result.modified_at.timestamp()
                    if result.modified_at
                    else 0
                ),
                result.score,
            ),
            reverse=True,
        )

    #
    # 일반 검색
    #
    else:

        scored_results.sort(
            key=lambda result: (
                result.score,
                (
                    result.modified_at.timestamp()
                    if result.modified_at
                    else 0
                ),
            ),
            reverse=True,
        )

    total = len(
        scored_results
    )

    total_pages = (
        math.ceil(
            total / page_size
        )
        if total > 0
        else 0
    )

    #
    # 존재하지 않는 페이지를 요청했을 경우
    # 마지막 페이지로 보정
    #
    if (
        total_pages > 0
        and page > total_pages
    ):
        page = total_pages

    start_index = (
        (page - 1)
        * page_size
    )

    end_index = (
        start_index
        + page_size
    )

    results = scored_results[
        start_index:end_index
    ]

    response_time_ms = int(
        (
            perf_counter()
            - started_at
        )
        * 1000
    )

    #
    # 검색 로그
    #
    search_log = SearchLog(
        query=(
            parsed_query.original_query
        ),
        normalized_query=(
            parsed_query.normalized_query
        ),
        result_count=total,
        response_time_ms=(
            response_time_ms
        ),
        searched_at=utc_now(),
    )

    db.add(
        search_log
    )

    db.commit()

    return SearchResponse(
        query=(
            parsed_query.original_query
        ),
        normalized_query=(
            parsed_query.normalized_query
        ),
        keywords=(
            parsed_query.keywords
        ),
        extensions=sorted(
            extension_filter
        ),
        year=(
            parsed_query.year
        ),
        recent=(
            parsed_query.recent
        ),
        file_type=(
            file_type
            if file_type != "all"
            else None
        ),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=results,
        response_time_ms=(
            response_time_ms
        ),
    )