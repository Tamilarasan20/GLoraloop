from datetime import datetime

from pydantic import BaseModel, HttpUrl

from app.schemas.brand_kit import BrandKit, TemplateReadyData


class SaveProjectRequest(BaseModel):
    name: str
    source_url: HttpUrl
    brand_kit: BrandKit
    templates: list[TemplateReadyData]


class SavedProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    source_url: str
    brand_kit: BrandKit
    templates: list[TemplateReadyData]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
