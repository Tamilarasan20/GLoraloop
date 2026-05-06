from app.schemas.brand_kit import ScrapedBrandData, ScrapedImage
from app.services.brand_intelligence import BrandIntelligenceService


def test_extract_brand_kit_returns_normalized_campaign_context() -> None:
    service = BrandIntelligenceService()
    scraped = ScrapedBrandData(
        url="https://example.com",
        final_url="https://example.com",
        title="Acme Studio | Home",
        meta_description="Premium handcrafted ceramic mugs for modern homes.",
        hero_text="Premium mugs crafted for slow mornings.",
        headings=["Premium mugs", "Shop handcrafted ceramics"],
        colors=["#123456", "#ffffff", "#f97316"],
        font_families=["Georgia", "Inter"],
        images=[
            ScrapedImage(
                url="https://example.com/mug.jpg",
                alt="Ceramic mug",
                width=1200,
                height=800,
            )
        ],
    )

    brand_kit = service.extract_brand_kit(scraped)

    assert brand_kit.brand_name == "Acme Studio"
    assert brand_kit.colors == ["#123456", "#ffffff", "#f97316"]
    assert brand_kit.font_style == "editorial serif"
    assert "premium" in brand_kit.tone
    assert brand_kit.images == ["https://example.com/mug.jpg"]


def test_campaign_and_template_generation_stays_canvas_ready() -> None:
    service = BrandIntelligenceService()
    scraped = ScrapedBrandData(
        url="https://example.com",
        final_url="https://example.com",
        title="Example",
        colors=["#111827", "#ffffff", "#2563eb"],
    )
    brand_kit = service.extract_brand_kit(scraped)

    campaigns = service.generate_campaign_concepts(brand_kit)
    templates = service.generate_template_data(brand_kit, campaigns)

    assert len(campaigns) == 3
    assert len(templates) == 3
    assert templates[0].canvas_width == 1080
    assert templates[0].layers[0].type == "image"
    assert any(layer.type == "text" for layer in templates[0].layers)


def test_modern_sans_serif_maps_to_inter() -> None:
    service = BrandIntelligenceService()

    assert service._canvas_font_family("modern sans-serif") == "Inter"
