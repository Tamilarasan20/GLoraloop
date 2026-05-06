from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routes.brand_kits import router as brand_kits_router
from app.routes.jobs import router as jobs_router
from app.routes.projects import router as projects_router
from app.routes.publishing import router as publishing_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title="Laraloop Brand DNA Extractor",
    version="0.1.0",
    description="Backend for extracting brand context and campaign-ready JSON from a business URL.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(brand_kits_router, prefix="/v1")
app.include_router(jobs_router, prefix="/v1")
app.include_router(projects_router, prefix="/v1")
app.include_router(publishing_router, prefix="/v1")
