from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app
from app.schemas.brand_kit import (
    BrandAnalysisResponse,
    BrandKit,
    CampaignConcept,
    ScrapedBrandData,
    StrategyDocument,
    TemplateReadyData,
)
from app.services.document_enrichment import HeuristicStrategyDocumentProvider
from app.services.knowledge_base_builder import KnowledgeBaseBuilder


def test_knowledge_base_builder_creates_reference_repo_shape() -> None:
    analysis = sample_analysis()
    builder = KnowledgeBaseBuilder()

    enriched = builder.enriched_data(analysis.brand_kit)
    guidelines = builder.brand_guidelines(analysis)
    memory = builder.brand_memory(analysis)
    business_profile, market_research, social_strategy = builder.documents(analysis)

    assert enriched["brandName"] == "Better Example"
    assert guidelines["colors"][0]["usage"] == "primary"
    assert "contentPillars" in memory
    assert business_profile.startswith("# Business Profile")
    assert market_research.startswith("# Market Research")
    assert social_strategy.startswith("# Social Media Strategy")


def test_save_knowledge_base_endpoint_persists_documents_and_assets() -> None:
    init_db()
    client = TestClient(app)
    response = client.post(
        "/v1/knowledge-bases",
        headers={"Authorization": "Bearer founder@laraloop.local"},
        json={
            "source_url": "https://example.com",
            "analysis": sample_analysis().model_dump(mode="json"),
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["business_name"] == "Better Example"
    assert data["business_profile"].startswith("# Business Profile")
    assert any(asset["type"] == "screenshot" for asset in data["visual_assets"])

    patch = client.patch(
        f"/v1/knowledge-bases/{data['id']}/documents/social_strategy",
        headers={"Authorization": "Bearer founder@laraloop.local"},
        json={"content": "# Social Media Strategy\n\n- Updated"},
    )
    assert patch.status_code == 200
    assert "Updated" in patch.json()["social_strategy"]


def sample_analysis() -> BrandAnalysisResponse:
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
        headings=["Original Tempeh", "Smoky Tempeh"],
        screenshot_path="/artifacts/example-screenshot.png",
    )
    strategy = run_async(HeuristicStrategyDocumentProvider().create(brand_kit, scraped))
    return BrandAnalysisResponse(
        brand_kit=brand_kit,
        campaign_concepts=[
            CampaignConcept(
                name="Protein Proof",
                objective="Awareness",
                angle="Protein proof",
                headline="Protein, Made Simple",
                subheadline="Plant-based protein for everyday meals.",
                cta="Shop Now",
                channels=["Instagram"],
            )
        ],
        template_ready_data=[
            TemplateReadyData(
                layout="modern-centered",
                headline="Protein, Made Simple",
                subheadline="Plant-based protein for everyday meals.",
                cta="Shop Now",
                layers=[],
            )
        ],
        scraped_data=scraped,
        strategy_document=StrategyDocument.model_validate(strategy.model_dump(mode="json")),
        strategy_pdf_url="/artifacts/better-example.pdf",
    )


def run_async(awaitable):
    import asyncio

    return asyncio.run(awaitable)
