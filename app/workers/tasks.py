import asyncio

from app.celery_app import celery_app
from app.db import SessionLocal, init_db
from app.models import JobStatus
from app.repositories import JobRepository
from app.services.pipeline import BrandDnaPipeline


@celery_app.task(name="brand_analysis.run")
def run_brand_analysis_job(job_id: str) -> str:
    init_db()
    db = SessionLocal()
    repo = JobRepository(db)

    try:
        job = repo.get(job_id)
        if job is None:
            raise ValueError(f"Job {job_id} was not found.")

        repo.update_status(job_id, JobStatus.RUNNING, "scraping", 15)
        result = asyncio.run(BrandDnaPipeline().analyze_with_strategy_document(job.url))
        repo.update_status(
            job_id,
            JobStatus.SUCCEEDED,
            "completed",
            100,
            result=result.model_dump(mode="json"),
        )
        return job_id
    except Exception as exc:
        repo.update_status(job_id, JobStatus.FAILED, "failed", 100, error=str(exc))
        raise
    finally:
        db.close()
