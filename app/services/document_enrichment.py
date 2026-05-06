import json
from abc import ABC, abstractmethod

from app.config import settings
from app.schemas.brand_kit import (
    BrandKit,
    BusinessProfile,
    BrandGuidelines,
    ExtractedAsset,
    MarketResearch,
    ScrapedBrandData,
    SocialPlatformPlan,
    SocialStrategy,
    StrategyDocument,
)


class StrategyDocumentProvider(ABC):
    @abstractmethod
    async def create(self, brand_kit: BrandKit, scraped: ScrapedBrandData) -> StrategyDocument:
        raise NotImplementedError


class HeuristicStrategyDocumentProvider(StrategyDocumentProvider):
    async def create(self, brand_kit: BrandKit, scraped: ScrapedBrandData) -> StrategyDocument:
        assets = self._assets(brand_kit, scraped)
        brand_name = brand_kit.brand_name
        primary_color = brand_kit.colors[0] if brand_kit.colors else "#111827"
        secondary_color = brand_kit.colors[1] if len(brand_kit.colors) > 1 else "#ffffff"
        accent_color = brand_kit.colors[2] if len(brand_kit.colors) > 2 else primary_color

        return StrategyDocument(
            title=f"{brand_name} - Brand Strategy Document",
            business_profile=BusinessProfile(
                overview=brand_kit.summary,
                products_or_services=self._products_or_services(scraped),
                key_selling_points=self._selling_points(brand_kit, scraped),
                retail_or_distribution=self._distribution(scraped),
                target_audience=[brand_kit.audience, *brand_kit.tone],
                founder_story=self._founder_story(scraped),
                marketing_goals=["Grow social reach", "Convert website visitors", "Turn brand proof into repeatable campaign assets"],
                website=scraped.final_url or scraped.url,
            ),
            social_strategy=SocialStrategy(
                priority_platforms=[
                    SocialPlatformPlan(
                        platform="TikTok",
                        priority=1,
                        role="Fast awareness through short-form educational and founder-led content.",
                        format_priority=["short video", "trend response", "comment reply"],
                        posting_cadence="4-5 posts per week",
                    ),
                    SocialPlatformPlan(
                        platform="Instagram",
                        priority=2,
                        role="Brand presence, Reels, UGC, product education, and social proof.",
                        format_priority=["Reels", "carousels", "Stories"],
                        posting_cadence="4 posts per week",
                    ),
                    SocialPlatformPlan(
                        platform="LinkedIn",
                        priority=3,
                        role="Founder credibility, partnerships, hiring, retail, and investor visibility.",
                        format_priority=["founder posts", "milestone posts", "industry POV"],
                        posting_cadence="2 posts per week",
                    ),
                ],
                content_pillars=[
                    "Proof-led benefit education",
                    "Product or service demos",
                    "Founder and origin story",
                    "Customer proof and testimonials",
                    "Objection handling and FAQs",
                ],
                messaging_hierarchy=[
                    brand_kit.campaign_angles[1] if len(brand_kit.campaign_angles) > 1 else "Lead with the clearest product benefit.",
                    "Use the brand tone consistently: " + ", ".join(brand_kit.tone),
                    "Turn trust signals into visible proof points.",
                ],
                quick_wins=[
                    "Pin a simple 'what we do' explainer video on every social profile.",
                    "Turn testimonials and review language into quote graphics.",
                    "Film the founder explaining the origin story in under 45 seconds.",
                    "Repurpose top website headings into short-form hooks.",
                ],
            ),
            market_research=MarketResearch(
                market_opportunity=[
                    f"{brand_name} can use its existing website messaging to create repeated campaign angles.",
                    "Consumers respond well to clear benefit proof, founder credibility, and specific use cases.",
                    "Short-form social can turn education into discoverability when the category needs explanation.",
                ],
                trend_tailwinds=[
                    "Founder-led brands are outperforming faceless brand accounts on trust.",
                    "Educational short-form content keeps working when it solves a real buyer question.",
                    "UGC and review-led creative reduce perceived risk before purchase.",
                ],
                competitive_landscape=[
                    "Direct competitors will likely compete on price, familiarity, or convenience.",
                    f"{brand_name}'s edge should be sharpened around positioning: {brand_kit.positioning}",
                    "The clearest white space is specific proof, not generic brand claims.",
                ],
                key_risks=[
                    "If the product category is unfamiliar, education must be repeated frequently.",
                    "Generic AI visuals can weaken trust unless grounded in real brand assets.",
                    "Organic reach is unstable; build reusable creative for paid and owned channels too.",
                ],
                social_platform_insights=[
                    "TikTok: best for fast testing of hooks and demos.",
                    "Instagram: best for brand consistency, Reels, Stories, and UGC proof.",
                    "LinkedIn: best for founder voice, partnerships, and business credibility.",
                ],
                target_audiences_on_social=[
                    "Problem-aware shoppers looking for a better option.",
                    "Existing category buyers comparing alternatives.",
                    "People who need education before they trust the offer.",
                ],
            ),
            brand_guidelines=BrandGuidelines(
                brand_personality=brand_kit.tone,
                color_palette={"primary": primary_color, "secondary": secondary_color, "accent": accent_color},
                typography={"recommended_heading": brand_kit.font_style, "recommended_body": "clean sans-serif"},
                design_style=[
                    "Use high contrast layouts.",
                    "Keep claims short and proof-led.",
                    "Use real scraped imagery where quality is high.",
                    "Keep templates consistent with extracted brand colors.",
                ],
                logo_url=brand_kit.logo_url,
                social_content_principles=[
                    "Lead with the strongest benefit.",
                    "Show the product, result, or use case quickly.",
                    "Use customer language whenever possible.",
                    "Repeat the origin or founder proof often enough to become memorable.",
                ],
            ),
            extracted_assets=assets,
        )

    def _assets(self, brand_kit: BrandKit, scraped: ScrapedBrandData) -> list[ExtractedAsset]:
        assets: list[ExtractedAsset] = []
        if brand_kit.logo_url:
            assets.append(ExtractedAsset(type="logo", url=brand_kit.logo_url, notes="Logo candidate extracted from website."))
        if scraped.screenshot_path:
            assets.append(ExtractedAsset(type="screenshot", url=scraped.screenshot_path, notes="Full-page screenshot captured during scrape."))
        for image in scraped.images[:20]:
            assets.append(
                ExtractedAsset(
                    type="image",
                    url=image.url,
                    alt=image.alt,
                    width=image.width,
                    height=image.height,
                    notes="Scraped website image asset.",
                )
            )
        return assets

    def _products_or_services(self, scraped: ScrapedBrandData) -> list[str]:
        headings = [heading for heading in scraped.headings if len(heading) < 90]
        return headings[:6] or ["Primary product or service inferred from website content."]

    def _selling_points(self, brand_kit: BrandKit, scraped: ScrapedBrandData) -> list[str]:
        points = [*brand_kit.campaign_angles, *scraped.ctas]
        return points[:8] or ["Clear offer", "Brand-consistent visual identity", "Website-supported proof points"]

    def _distribution(self, scraped: ScrapedBrandData) -> list[str]:
        distribution_terms = ("stocked", "available", "shipping", "retail", "store", "shop", "book", "contact")
        candidates = [text for text in [scraped.meta_description or "", scraped.hero_text or "", *scraped.ctas] if any(term in text.lower() for term in distribution_terms)]
        return candidates[:5] or ["Website", "Social media", "Direct customer acquisition"]

    def _founder_story(self, scraped: ScrapedBrandData) -> str | None:
        story_terms = ("founder", "founded", "story", "mission", "about", "started")
        for text in [scraped.hero_text or "", scraped.meta_description or "", *scraped.headings]:
            if any(term in text.lower() for term in story_terms):
                return text
        return None


class OpenAIStrategyDocumentProvider(StrategyDocumentProvider):
    async def create(self, brand_kit: BrandKit, scraped: ScrapedBrandData) -> StrategyDocument:
        if not settings.openai_api_key:
            return await HeuristicStrategyDocumentProvider().create(brand_kit, scraped)

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You create investor-grade marketing strategy documents. Return strict JSON matching "
                        "StrategyDocument: title, business_profile, social_strategy, market_research, "
                        "brand_guidelines, extracted_assets. Be specific, practical, and campaign-ready."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "brand_kit": brand_kit.model_dump(mode="json"),
                            "scraped_data": scraped.model_dump(mode="json"),
                        },
                        ensure_ascii=True,
                    ),
                },
            ],
        )
        content = response.choices[0].message.content or "{}"
        try:
            return StrategyDocument.model_validate_json(content)
        except Exception:
            return await HeuristicStrategyDocumentProvider().create(brand_kit, scraped)


class GeminiStrategyDocumentProvider(StrategyDocumentProvider):
    async def create(self, brand_kit: BrandKit, scraped: ScrapedBrandData) -> StrategyDocument:
        if not settings.gemini_api_key:
            return await HeuristicStrategyDocumentProvider().create(brand_kit, scraped)

        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        prompt = (
            "Create strict JSON matching StrategyDocument: title, business_profile, social_strategy, "
            "market_research, brand_guidelines, extracted_assets. Use the Better Nature example style: "
            "clear headings, specific bullets, practical strategy. Data:\n"
            + json.dumps(
                {
                    "brand_kit": brand_kit.model_dump(mode="json"),
                    "scraped_data": scraped.model_dump(mode="json"),
                },
                ensure_ascii=True,
            )
        )
        response = await model.generate_content_async(prompt)
        try:
            return StrategyDocument.model_validate_json(response.text)
        except Exception:
            return await HeuristicStrategyDocumentProvider().create(brand_kit, scraped)


def get_strategy_document_provider() -> StrategyDocumentProvider:
    provider = settings.ai_provider.lower()
    if provider == "openai":
        return OpenAIStrategyDocumentProvider()
    if provider == "gemini":
        return GeminiStrategyDocumentProvider()
    return HeuristicStrategyDocumentProvider()
