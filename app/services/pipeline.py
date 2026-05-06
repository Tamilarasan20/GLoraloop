from pydantic import HttpUrl

from app.schemas.brand_kit import BrandAnalysisResponse
from app.services.ai_providers import get_brand_extraction_provider
from app.services.brand_intelligence import BrandIntelligenceService
from app.services.scraper import PlaywrightScraper
from app.services.storage import AssetStorageService
from app.services.strategy_pipeline import StrategyDocumentPipeline


class BrandDnaPipeline:
    def __init__(
        self,
        scraper: PlaywrightScraper | None = None,
        intelligence: BrandIntelligenceService | None = None,
    ) -> None:
        self.scraper = scraper or PlaywrightScraper()
        self.intelligence = intelligence or BrandIntelligenceService()
        self.brand_provider = get_brand_extraction_provider()
        self.storage = AssetStorageService()

    async def analyze(self, url: HttpUrl) -> BrandAnalysisResponse:
        return await self.analyze_url(str(url))

    async def analyze_url(self, url: str) -> BrandAnalysisResponse:
        scraped_data = await self.scraper.scrape(str(url))
        if scraped_data.screenshot_path:
            scraped_data.screenshot_path = self.storage.upload_file(
                scraped_data.screenshot_path,
                content_type="image/png",
            )
        brand_kit = await self.brand_provider.extract_brand_kit(scraped_data)
        campaign_concepts = self.intelligence.generate_campaign_concepts(brand_kit)
        template_ready_data = self.intelligence.generate_template_data(brand_kit, campaign_concepts)

        return BrandAnalysisResponse(
            brand_kit=brand_kit,
            campaign_concepts=campaign_concepts,
            template_ready_data=template_ready_data,
            scraped_data=scraped_data,
        )

    async def analyze_with_strategy_document(self, url: str) -> BrandAnalysisResponse:
        analysis = await self.analyze_url(url)
        return await StrategyDocumentPipeline().enrich(analysis)
