from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.search import router as search_router
from app.api.admin import router as admin_router
from app.database.database import create_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield


app = FastAPI(
    title="사내 파일검색 챗봇 API",
    description="사내 파일 및 폴더 검색을 위한 Backend API",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(search_router)
app.include_router(admin_router)


@app.get("/")
def root() -> dict:
    return {
        "service": "internal-file-search",
        "status": "running",
    }