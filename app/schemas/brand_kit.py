from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, field_validator


class LayoutName(str, Enum):
    MODERN_CENTERED = "modern-centered"
    TEXT_OVERLAY_BOTTOM = "text-overlay-bottom"
    IMAGE_LEFT_TEXT_RIGHT = "image-left-text-right"


class AnalyzeBrandRequest(BaseModel):
    url: HttpUrl


class ScrapedImage(BaseModel):
    url: str
    alt: str | None = None
    width: int | None = None
    height: int | None = None
    is_logo_candidate: bool = False


class ScrapedBrandData(BaseModel):
    url: str
    final_url: str
    title: str | None = None
    meta_description: str | None = None
    hero_text: str | None = None
    headings: list[str] = Field(default_factory=list)
    ctas: list[str] = Field(default_factory=list)
    testimonials: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    font_families: list[str] = Field(default_factory=list)
    logo_url: str | None = None
    images: list[ScrapedImage] = Field(default_factory=list)
    screenshot_path: str | None = None


class CampaignConcept(BaseModel):
    name: str
    objective: str
    angle: str
    headline: str
    subheadline: str
    cta: str
    channels: list[str]


class TemplateLayer(BaseModel):
    type: str
    content: str | None = None
    src: str | None = None
    color: str | None = None
    font_family: str | None = None
    font_size: int | None = None
    x: int
    y: int
    width: int | None = None
    height: int | None = None
    z_index: int


class TemplateReadyData(BaseModel):
    canvas_width: int = 1080
    canvas_height: int = 1080
    layout: LayoutName
    headline: str
    subheadline: str
    background_image: str | None = None
    cta: str
    layers: list[TemplateLayer]


class BrandKit(BaseModel):
    brand_name: str
    summary: str
    audience: str
    tone: list[str]
    colors: list[str]
    font_style: str
    logo_url: str | None = None
    images: list[str]
    positioning: str
    campaign_angles: list[str]

    @field_validator("colors")
    @classmethod
    def require_hex_colors(cls, colors: list[str]) -> list[str]:
        for color in colors:
            if not color.startswith("#") or len(color) not in {4, 7}:
                raise ValueError(f"Invalid hex color: {color}")
        return colors


class BrandAnalysisResponse(BaseModel):
    brand_kit: BrandKit
    campaign_concepts: list[CampaignConcept]
    template_ready_data: list[TemplateReadyData]
    scraped_data: ScrapedBrandData
    strategy_document: "StrategyDocument | None" = None
    strategy_pdf_url: str | None = None


class ExtractedAsset(BaseModel):
    type: str
    url: str
    alt: str | None = None
    width: int | None = None
    height: int | None = None
    notes: str | None = None


class BusinessProfile(BaseModel):
    overview: str
    products_or_services: list[str]
    key_selling_points: list[str]
    retail_or_distribution: list[str]
    target_audience: list[str]
    founder_story: str | None = None
    marketing_goals: list[str]
    website: str


class SocialPlatformPlan(BaseModel):
    platform: str
    priority: int
    role: str
    format_priority: list[str]
    posting_cadence: str


class SocialStrategy(BaseModel):
    priority_platforms: list[SocialPlatformPlan]
    content_pillars: list[str]
    messaging_hierarchy: list[str]
    quick_wins: list[str]


class MarketResearch(BaseModel):
    market_opportunity: list[str]
    trend_tailwinds: list[str]
    competitive_landscape: list[str]
    key_risks: list[str]
    social_platform_insights: list[str]
    target_audiences_on_social: list[str]


class BrandGuidelines(BaseModel):
    brand_personality: list[str]
    color_palette: dict[str, str]
    typography: dict[str, str]
    design_style: list[str]
    logo_url: str | None = None
    social_content_principles: list[str]


class StrategyDocument(BaseModel):
    title: str
    business_profile: BusinessProfile
    social_strategy: SocialStrategy
    market_research: MarketResearch
    brand_guidelines: BrandGuidelines
    extracted_assets: list[ExtractedAsset]
