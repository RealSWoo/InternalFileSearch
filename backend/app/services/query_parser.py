import re
from dataclasses import dataclass
from datetime import datetime, timezone


STOPWORDS = {
    "찾아줘",
    "찾아",
    "검색해줘",
    "검색해",
    "검색",
    "보여줘",
    "보여",
    "알려줘",
    "알려",
    "좀",
    "파일",
    "자료",
    "문서",
    "있는",
    "있어",
    "있나요",
    "있니",
    "관련",
    "관련된",
}


RECENT_KEYWORDS = {
    "최근",
    "최신",
    "최신본",
    "최근본",
}


EXTENSION_ALIASES = {
    "ppt": {"ppt", "pptx"},
    "pptx": {"pptx"},
    "파워포인트": {"ppt", "pptx"},
    "피피티": {"ppt", "pptx"},

    "excel": {"xls", "xlsx"},
    "엑셀": {"xls", "xlsx"},
    "xlsx": {"xlsx"},
    "xls": {"xls"},

    "word": {"doc", "docx"},
    "워드": {"doc", "docx"},
    "doc": {"doc"},
    "docx": {"docx"},

    "pdf": {"pdf"},

    "한글": {"hwp", "hwpx"},
    "hwp": {"hwp"},
    "hwpx": {"hwpx"},

    "csv": {"csv"},
    "txt": {"txt"},
    "텍스트": {"txt"},

    "jpg": {"jpg", "jpeg"},
    "jpeg": {"jpg", "jpeg"},
    "이미지": {"jpg", "jpeg", "png"},
    "사진": {"jpg", "jpeg", "png"},
    "png": {"png"},

    "zip": {"zip"},
    "압축": {"zip"},
}


@dataclass
class ParsedQuery:
    original_query: str
    normalized_query: str
    keywords: list[str]
    extensions: set[str]

    year: int | None = None
    recent: bool = False


def normalize_query(query: str) -> str:
    query = query.strip().lower()

    query = re.sub(
        r"[_\-/\\.,()\[\]{}]+",
        " ",
        query,
    )

    query = re.sub(
        r"\s+",
        " ",
        query,
    )

    return query.strip()


def get_current_year() -> int:
    return datetime.now(
        timezone.utc
    ).year


def parse_query(query: str) -> ParsedQuery:
    original_query = query.strip()
    normalized_query = normalize_query(query)

    if not normalized_query:
        return ParsedQuery(
            original_query=original_query,
            normalized_query="",
            keywords=[],
            extensions=set(),
        )

    tokens = normalized_query.split()

    keywords: list[str] = []
    extensions: set[str] = set()

    year: int | None = None
    recent = False

    current_year = get_current_year()

    for token in tokens:

        # 최근 / 최신
        if token in RECENT_KEYWORDS:
            recent = True
            continue

        # 올해
        if token in {
            "올해",
            "금년",
        }:
            year = current_year
            continue

        # 작년 / 지난해
        if token in {
            "작년",
            "지난해",
        }:
            year = current_year - 1
            continue

        # 숫자 연도
        year_match = re.fullmatch(
            r"(19|20)\d{2}년?",
            token,
        )

        if year_match:
            year = int(
                token.replace("년", "")
            )
            continue

        # 불용어
        if token in STOPWORDS:
            continue

        # 확장자
        if token in EXTENSION_ALIASES:
            extensions.update(
                EXTENSION_ALIASES[token]
            )
            continue

        keywords.append(token)

    keywords = list(
        dict.fromkeys(keywords)
    )

    return ParsedQuery(
        original_query=original_query,
        normalized_query=" ".join(keywords),
        keywords=keywords,
        extensions=extensions,
        year=year,
        recent=recent,
    )