import json
from abc import ABC, abstractmethod

from app.config import settings
from app.schemas.brand_kit import BrandKit, ScrapedBrandData
from app.services.brand_intelligence import BrandIntelligenceService


class BrandExtractionProvider(ABC):
    @abstractmethod
    async def extract_brand_kit(self, scraped: ScrapedBrandData) -> BrandKit:
        raise NotImplementedError


class HeuristicBrandExtractionProvider(BrandExtractionProvider):
    async def extract_brand_kit(self, scraped: ScrapedBrandData) -> BrandKit:
        return BrandIntelligenceService().extract_brand_kit(scraped)


class OpenAIBrandExtractionProvider(BrandExtractionProvider):
    async def extract_brand_kit(self, scraped: ScrapedBrandData) -> BrandKit:
        if not settings.openai_api_key:
            return await HeuristicBrandExtractionProvider().extract_brand_kit(scraped)

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior brand strategist. Return strict JSON matching this shape: "
                        "{brand_name, summary, audience, tone, colors, font_style, logo_url, images, positioning, campaign_angles}."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(scraped.model_dump(mode="json"), ensure_ascii=True),
                },
            ],
        )
        content = response.choices[0].message.content or "{}"
        return BrandKit.model_validate_json(content)


class GeminiBrandExtractionProvider(BrandExtractionProvider):
    async def extract_brand_kit(self, scraped: ScrapedBrandData) -> BrandKit:
        if not settings.gemini_api_key:
            return await HeuristicBrandExtractionProvider().extract_brand_kit(scraped)

        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        prompt = (
            "Return strict JSON for a marketing BrandKit with keys: brand_name, summary, audience, "
            "tone, colors, font_style, logo_url, images, positioning, campaign_angles.\n\n"
            f"Scraped data:\n{json.dumps(scraped.model_dump(mode='json'), ensure_ascii=True)}"
        )
        response = await model.generate_content_async(prompt)
        return BrandKit.model_validate_json(response.text)


def get_brand_extraction_provider() -> BrandExtractionProvider:
    provider = settings.ai_provider.lower()
    if provider == "openai":
        return OpenAIBrandExtractionProvider()
    if provider == "gemini":
        return GeminiBrandExtractionProvider()
    return HeuristicBrandExtractionProvider()
