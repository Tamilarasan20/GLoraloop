from app.schemas.brand_kit import BrandAnalysisResponse
from app.services.document_enrichment import get_strategy_document_provider
from app.services.pdf_document import StrategyPdfService
from app.services.storage import AssetStorageService


class StrategyDocumentPipeline:
    def __init__(self) -> None:
        self.provider = get_strategy_document_provider()
        self.pdf = StrategyPdfService()
        self.storage = AssetStorageService()

    async def enrich(self, analysis: BrandAnalysisResponse) -> BrandAnalysisResponse:
        document = await self.provider.create(analysis.brand_kit, analysis.scraped_data)
        pdf_path = self.pdf.render(document)
        pdf_url = self.storage.upload_file(pdf_path, content_type="application/pdf")
        analysis.strategy_document = document
        analysis.strategy_pdf_url = pdf_url
        return analysis
