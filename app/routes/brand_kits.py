from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.repositories import JobRepository
from app.schemas.brand_kit import AnalyzeBrandRequest, BrandAnalysisResponse
from app.schemas.jobs import BrandAnalysisJobResponse, CreateBrandAnalysisJobRequest
from app.services.pipeline import BrandDnaPipeline
from app.workers.tasks import run_brand_analysis_job


router = APIRouter(prefix="/brand-kits", tags=["brand-kits"])


@router.post("/analyze", response_model=BrandAnalysisResponse)
async def analyze_brand_kit(request: AnalyzeBrandRequest) -> BrandAnalysisResponse:
    pipeline = BrandDnaPipeline()

    try:
        return await pipeline.analyze(request.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc


@router.post("/jobs", response_model=BrandAnalysisJobResponse, status_code=202)
async def create_brand_analysis_job(
    request: CreateBrandAnalysisJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> BrandAnalysisJobResponse:
    job = JobRepository(db).create(str(request.url))

    if settings.celery_always_eager:
        background_tasks.add_task(run_brand_analysis_job.run, job.id)
        return BrandAnalysisJobResponse.model_validate(job)

    try:
        run_brand_analysis_job.delay(job.id)
    except Exception:
        background_tasks.add_task(run_brand_analysis_job.run, job.id)

    return BrandAnalysisJobResponse.model_validate(job)
