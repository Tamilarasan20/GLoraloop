from app.schemas.brand_kit import BrandAnalysisResponse, BrandKit, StrategyDocument


class KnowledgeBaseBuilder:
    def enriched_data(self, brand_kit: BrandKit) -> dict:
        return {
            "brandName": brand_kit.brand_name,
            "businessOverview": brand_kit.summary,
            "brandValues": brand_kit.tone,
            "brandAesthetic": brand_kit.font_style,
            "toneOfVoice": ", ".join(brand_kit.tone),
            "tagline": brand_kit.positioning,
            "logoUrl": brand_kit.logo_url,
            "campaignAngles": brand_kit.campaign_angles,
        }

    def brand_guidelines(self, analysis: BrandAnalysisResponse) -> dict:
        brand_kit = analysis.brand_kit
        strategy = analysis.strategy_document
        color_roles = ["primary", "secondary", "accent", "background"]
        colors = [
            {"hex": color, "usage": color_roles[index] if index < len(color_roles) else f"color_{index + 1}"}
            for index, color in enumerate(brand_kit.colors)
        ]
        typography = [
            {"family": brand_kit.font_style, "usage": "headings"},
            {"family": "clean sans-serif", "usage": "body"},
        ]
        if strategy:
            colors = [{"hex": value, "usage": key} for key, value in strategy.brand_guidelines.color_palette.items()]
            typography = [
                {"family": value, "usage": key}
                for key, value in strategy.brand_guidelines.typography.items()
            ]

        return {
            "colors": colors,
            "typography": typography,
            "logos": [{"url": brand_kit.logo_url}] if brand_kit.logo_url else [],
            "images": brand_kit.images,
            "personality": strategy.brand_guidelines.brand_personality if strategy else brand_kit.tone,
            "principles": strategy.brand_guidelines.social_content_principles if strategy else brand_kit.campaign_angles,
        }

    def brand_memory(self, analysis: BrandAnalysisResponse) -> dict:
        strategy = analysis.strategy_document
        return {
            "voice": analysis.brand_kit.tone,
            "positioning": analysis.brand_kit.positioning,
            "contentPillars": strategy.social_strategy.content_pillars if strategy else [],
            "messagingHierarchy": strategy.social_strategy.messaging_hierarchy if strategy else analysis.brand_kit.campaign_angles,
            "quickWins": strategy.social_strategy.quick_wins if strategy else [],
            "risks": strategy.market_research.key_risks if strategy else [],
        }

    def documents(self, analysis: BrandAnalysisResponse) -> tuple[str, str, str]:
        strategy = analysis.strategy_document
        if strategy is None:
            fallback = analysis.brand_kit.summary
            return fallback, "\n".join(analysis.brand_kit.campaign_angles), "\n".join(analysis.brand_kit.campaign_angles)

        return (
            self._business_profile(strategy),
            self._market_research(strategy),
            self._social_strategy(strategy),
        )

    def visual_assets(self, analysis: BrandAnalysisResponse) -> list[dict]:
        if analysis.strategy_document:
            return [asset.model_dump(mode="json") for asset in analysis.strategy_document.extracted_assets]
        assets = []
        if analysis.brand_kit.logo_url:
            assets.append({"type": "logo", "url": analysis.brand_kit.logo_url})
        assets.extend({"type": "image", "url": image} for image in analysis.brand_kit.images)
        if analysis.scraped_data.screenshot_path:
            assets.append({"type": "screenshot", "url": analysis.scraped_data.screenshot_path})
        return assets

    def _business_profile(self, strategy: StrategyDocument) -> str:
        profile = strategy.business_profile
        return self._markdown(
            "Business Profile",
            [
                ("Overview", [profile.overview]),
                ("Products / Services", profile.products_or_services),
                ("Key Selling Points", profile.key_selling_points),
                ("Retail / Distribution", profile.retail_or_distribution),
                ("Target Audience", profile.target_audience),
                ("Founder Story", [profile.founder_story or "Not clearly found."]),
                ("Marketing Goals", profile.marketing_goals),
                ("Website", [profile.website]),
            ],
        )

    def _market_research(self, strategy: StrategyDocument) -> str:
        research = strategy.market_research
        return self._markdown(
            "Market Research",
            [
                ("Market Opportunity", research.market_opportunity),
                ("Trend Tailwinds", research.trend_tailwinds),
                ("Competitive Landscape", research.competitive_landscape),
                ("Key Risks", research.key_risks),
                ("Social Platform Insights", research.social_platform_insights),
                ("Target Audiences on Social", research.target_audiences_on_social),
            ],
        )

    def _social_strategy(self, strategy: StrategyDocument) -> str:
        social = strategy.social_strategy
        platform_lines = [
            f"{plan.priority}. {plan.platform} - {plan.role} Cadence: {plan.posting_cadence}"
            for plan in social.priority_platforms
        ]
        return self._markdown(
            "Social Media Strategy",
            [
                ("Priority Platforms", platform_lines),
                ("Content Pillars", social.content_pillars),
                ("Messaging Hierarchy", social.messaging_hierarchy),
                ("Quick Wins", social.quick_wins),
            ],
        )

    def _markdown(self, title: str, sections: list[tuple[str, list[str]]]) -> str:
        lines = [f"# {title}", ""]
        for section, items in sections:
            lines.append(f"## {section}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
        return "\n".join(lines).strip()
