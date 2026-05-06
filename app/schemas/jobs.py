from datetime import datetime

from pydantic import BaseModel, HttpUrl

from app.models import JobStatus
from app.schemas.brand_kit import BrandAnalysisResponse


class CreateBrandAnalysisJobRequest(BaseModel):
    url: HttpUrl


class BrandAnalysisJobResponse(BaseModel):
    id: str
    url: str
    status: JobStatus
    progress: int
    stage: str
    error: str | None = None
    result: BrandAnalysisResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
