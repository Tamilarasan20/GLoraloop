from pydantic import HttpUrl

from app.schemas.brand_kit import BrandAnalysisResponse
from app.services.brand_intelligence import BrandIntelligenceService
from app.services.scraper import PlaywrightScraper


class BrandDnaPipeline:
    def __init__(
        self,
        scraper: PlaywrightScraper | None = None,
        intelligence: BrandIntelligenceService | None = None,
    ) -> None:
        self.scraper = scraper or PlaywrightScraper()
        self.intelligence = intelligence or BrandIntelligenceService()

    async def analyze(self, url: HttpUrl) -> BrandAnalysisResponse:
        scraped_data = await self.scraper.scrape(str(url))
        brand_kit = self.intelligence.extract_brand_kit(scraped_data)
        campaign_concepts = self.intelligence.generate_campaign_concepts(brand_kit)
        template_ready_data = self.intelligence.generate_template_data(brand_kit, campaign_concepts)

        return BrandAnalysisResponse(
            brand_kit=brand_kit,
            campaign_concepts=campaign_concepts,
            template_ready_data=template_ready_data,
            scraped_data=scraped_data,
        )
