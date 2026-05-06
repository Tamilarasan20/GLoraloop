from urllib.parse import urlparse

from app.schemas.brand_kit import (
    BrandKit,
    CampaignConcept,
    LayoutName,
    ScrapedBrandData,
    TemplateLayer,
    TemplateReadyData,
)


class BrandIntelligenceService:
    """Local deterministic intelligence layer.

    This is where OpenAI/Gemini structured extraction will be integrated.
    The deterministic first pass keeps the Sprint 1 API runnable without API keys.
    """

    def extract_brand_kit(self, scraped: ScrapedBrandData) -> BrandKit:
        brand_name = self._infer_brand_name(scraped)
        colors = (scraped.colors[:3] or ["#111827", "#ffffff", "#2563eb"])[:3]
        font_style = self._infer_font_style(scraped.font_families)
        summary = self._summary(scraped)
        audience = "People evaluating this business online based on its website messaging, offers, and visual identity."
        tone = self._infer_tone(scraped)
        images = [image.url for image in scraped.images[:8]]

        return BrandKit(
            brand_name=brand_name,
            summary=summary,
            audience=audience,
            tone=tone,
            colors=colors,
            font_style=font_style,
            logo_url=scraped.logo_url,
            images=images,
            positioning=f"{brand_name} presents itself as {', '.join(tone)} and focused on clear customer value.",
            campaign_angles=[
                "Promote a seasonal or limited-time offer",
                "Highlight the most visible product or service benefit",
                "Build trust with proof points, reviews, or guarantees",
            ],
        )

    def generate_campaign_concepts(self, brand_kit: BrandKit) -> list[CampaignConcept]:
        primary_tone = brand_kit.tone[0] if brand_kit.tone else "clear"
        return [
            CampaignConcept(
                name="Best Benefit Spotlight",
                objective="Drive consideration",
                angle=brand_kit.campaign_angles[1],
                headline=f"Discover {brand_kit.brand_name}",
                subheadline=f"{brand_kit.summary[:90].rstrip('.')}.",
                cta="Learn More",
                channels=["Facebook", "Instagram"],
            ),
            CampaignConcept(
                name="Trust Builder",
                objective="Increase confidence",
                angle=brand_kit.campaign_angles[2],
                headline="Made For Your Needs",
                subheadline=f"A {primary_tone} way to introduce what makes {brand_kit.brand_name} different.",
                cta="See Why",
                channels=["LinkedIn", "Facebook"],
            ),
            CampaignConcept(
                name="Fast Offer",
                objective="Generate action",
                angle=brand_kit.campaign_angles[0],
                headline="Start Today",
                subheadline=f"Bring {brand_kit.brand_name}'s offer to customers with a focused campaign.",
                cta="Get Started",
                channels=["Instagram", "Email"],
            ),
        ]

    def generate_template_data(
        self,
        brand_kit: BrandKit,
        campaign_concepts: list[CampaignConcept],
    ) -> list[TemplateReadyData]:
        background = brand_kit.images[0] if brand_kit.images else None
        font_family = self._canvas_font_family(brand_kit.font_style)
        primary_color = brand_kit.colors[0]
        accent_color = brand_kit.colors[2] if len(brand_kit.colors) > 2 else brand_kit.colors[0]

        templates: list[TemplateReadyData] = []
        for concept in campaign_concepts:
            templates.append(
                TemplateReadyData(
                    layout=LayoutName.MODERN_CENTERED,
                    headline=concept.headline,
                    subheadline=concept.subheadline,
                    background_image=background,
                    cta=concept.cta,
                    layers=[
                        TemplateLayer(type="image", src=background, x=0, y=0, width=1080, height=1080, z_index=0),
                        TemplateLayer(
                            type="rect",
                            color=primary_color,
                            x=80,
                            y=700,
                            width=920,
                            height=260,
                            z_index=1,
                        ),
                        TemplateLayer(
                            type="text",
                            content=concept.headline,
                            color="#ffffff",
                            font_family=font_family,
                            font_size=76,
                            x=130,
                            y=742,
                            width=820,
                            z_index=2,
                        ),
                        TemplateLayer(
                            type="text",
                            content=concept.subheadline,
                            color="#ffffff",
                            font_family=font_family,
                            font_size=34,
                            x=130,
                            y=835,
                            width=720,
                            z_index=3,
                        ),
                        TemplateLayer(
                            type="text",
                            content=concept.cta,
                            color=accent_color,
                            font_family=font_family,
                            font_size=30,
                            x=130,
                            y=910,
                            width=300,
                            z_index=4,
                        ),
                    ],
                )
            )
        return templates

    def _infer_brand_name(self, scraped: ScrapedBrandData) -> str:
        if scraped.title:
            return scraped.title.split("|")[0].split("-")[0].strip()[:60]

        host = urlparse(scraped.final_url or scraped.url).netloc.replace("www.", "")
        return host.split(".")[0].replace("-", " ").title()

    def _summary(self, scraped: ScrapedBrandData) -> str:
        source = scraped.meta_description or scraped.hero_text or "A business with a web presence and campaign-ready brand cues"
        return " ".join(source.split())[:220]

    def _infer_tone(self, scraped: ScrapedBrandData) -> list[str]:
        text = " ".join([scraped.hero_text or "", scraped.meta_description or "", *scraped.headings]).lower()
        tone = []
        if any(word in text for word in ["luxury", "premium", "crafted", "studio"]):
            tone.append("premium")
        if any(word in text for word in ["easy", "simple", "fast", "quick"]):
            tone.append("approachable")
        if any(word in text for word in ["trusted", "secure", "professional", "expert"]):
            tone.append("professional")
        if any(word in text for word in ["fun", "play", "creative", "fresh"]):
            tone.append("playful")

        return (tone + ["modern", "clear", "warm"])[:3]

    def _infer_font_style(self, fonts: list[str]) -> str:
        joined = " ".join(fonts).lower()
        if any(font in joined for font in ["serif", "georgia", "garamond", "times"]):
            return "editorial serif"
        if any(font in joined for font in ["mono", "code", "courier"]):
            return "technical monospace"
        if any(font in joined for font in ["rounded", "nunito", "quicksand"]):
            return "rounded sans-serif"
        return "modern sans-serif"

    def _canvas_font_family(self, font_style: str) -> str:
        if "sans-serif" in font_style or "sans serif" in font_style:
            return "Inter"
        if "serif" in font_style:
            return "Georgia"
        if "mono" in font_style:
            return "Courier New"
        return "Inter"
