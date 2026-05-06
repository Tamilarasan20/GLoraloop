from datetime import datetime
from enum import Enum

from pydantic import BaseModel, HttpUrl

from app.schemas.brand_kit import BrandAnalysisResponse, ExtractedAsset


class KnowledgeDocumentType(str, Enum):
    BUSINESS_PROFILE = "business_profile"
    MARKET_RESEARCH = "market_research"
    SOCIAL_STRATEGY = "social_strategy"


class SaveKnowledgeBaseRequest(BaseModel):
    source_url: HttpUrl
    analysis: BrandAnalysisResponse


class BuildKnowledgeBaseRequest(BaseModel):
    url: HttpUrl


class UpdateKnowledgeDocumentRequest(BaseModel):
    content: str


class KnowledgeBaseResponse(BaseModel):
    id: str
    user_id: str
    business_name: str
    website: str
    status: str
    scraped_data: dict
    enriched_data: dict
    brand_guidelines: dict
    brand_memory: dict
    visual_assets: list[ExtractedAsset]
    business_profile: str
    market_research: str
    social_strategy: str
    strategy_pdf_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
