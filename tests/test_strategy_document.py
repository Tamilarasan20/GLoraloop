from pathlib import Path

from app.schemas.brand_kit import BrandKit, ScrapedBrandData, ScrapedImage
from app.services.document_enrichment import HeuristicStrategyDocumentProvider
from app.services.pdf_document import StrategyPdfService


def test_strategy_document_includes_scraped_assets() -> None:
    brand_kit = BrandKit(
        brand_name="Better Example",
        summary="A plant-based food brand with strong protein and gut health positioning.",
        audience="Health-conscious shoppers",
        tone=["playful", "warm", "confident"],
        colors=["#e2dd30", "#006269", "#ee7415"],
        font_style="bold display",
        logo_url="https://example.com/logo.png",
        images=["https://example.com/product.png"],
        positioning="Founder-led whole food brand.",
        campaign_angles=["Protein proof", "Gut health education", "Founder story"],
    )
    scraped = ScrapedBrandData(
        url="https://example.com",
        final_url="https://example.com",
        title="Better Example",
        hero_text="Founder story and product education.",
        headings=["Original Tempeh", "Smoky Tempeh"],
        ctas=["Shop now"],
        screenshot_path="/artifacts/example-screenshot.png",
        images=[ScrapedImage(url="https://example.com/product.png", alt="Product", width=1000, height=800)],
    )

    document = run_async(HeuristicStrategyDocumentProvider().create(brand_kit, scraped))

    assert document.business_profile.products_or_services[:2] == ["Original Tempeh", "Smoky Tempeh"]
    assert document.brand_guidelines.logo_url == "https://example.com/logo.png"
    assert len(document.extracted_assets) == 3


def test_pdf_renderer_creates_file(tmp_path, monkeypatch) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "artifacts_dir", tmp_path)
    brand_kit = BrandKit(
        brand_name="Acme",
        summary="A clear product brand.",
        audience="Busy buyers",
        tone=["modern", "clear", "warm"],
        colors=["#111827", "#ffffff", "#2563eb"],
        font_style="modern sans-serif",
        images=[],
        positioning="Simple and useful.",
        campaign_angles=["Offer", "Benefit", "Trust"],
    )
    scraped = ScrapedBrandData(url="https://example.com", final_url="https://example.com", title="Acme")
    document = run_async(HeuristicStrategyDocumentProvider().create(brand_kit, scraped))

    path = StrategyPdfService().render(document)

    assert Path(path).exists()
    assert path.suffix == ".pdf"
    assert path.stat().st_size > 0


def run_async(awaitable):
    import asyncio

    return asyncio.run(awaitable)
