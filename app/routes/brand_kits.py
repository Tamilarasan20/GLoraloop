from fastapi import APIRouter, HTTPException

from app.schemas.brand_kit import AnalyzeBrandRequest, BrandAnalysisResponse
from app.services.pipeline import BrandDnaPipeline


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
