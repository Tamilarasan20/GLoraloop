from fastapi import APIRouter, HTTPException

from app.schemas.brand_kit import AnalyzeBrandRequest, BrandAnalysisResponse
from app.services.pipeline import BrandDnaPipeline
from app.services.strategy_pipeline import StrategyDocumentPipeline


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/strategy", response_model=BrandAnalysisResponse)
async def generate_strategy_document(request: AnalyzeBrandRequest) -> BrandAnalysisResponse:
    try:
        analysis = await BrandDnaPipeline().analyze(request.url)
        return await StrategyDocumentPipeline().enrich(analysis)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
