import asyncio

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.db import SessionLocal, get_db
from app.models import JobStatus
from app.repositories import JobRepository
from app.schemas.jobs import BrandAnalysisJobResponse


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=BrandAnalysisJobResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)) -> BrandAnalysisJobResponse:
    job = JobRepository(db).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return BrandAnalysisJobResponse.model_validate(job)


@router.websocket("/{job_id}/ws")
async def watch_job(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            db = SessionLocal()
            try:
                job = JobRepository(db).get(job_id)
                if job is None:
                    await websocket.send_json({"error": "Job not found"})
                    await websocket.close(code=1008)
                    return

                payload = BrandAnalysisJobResponse.model_validate(job).model_dump(mode="json")
                await websocket.send_json(payload)
                if job.status in {JobStatus.SUCCEEDED, JobStatus.FAILED}:
                    await websocket.close()
                    return
            finally:
                db.close()

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
