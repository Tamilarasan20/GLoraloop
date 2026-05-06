from pathlib import Path
from textwrap import wrap

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import settings
from app.schemas.brand_kit import StrategyDocument


class StrategyPdfService:
    def render(self, document: StrategyDocument) -> Path:
        settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
        safe_title = "".join(char.lower() if char.isalnum() else "-" for char in document.title).strip("-")[:80]
        path = settings.artifacts_dir / f"{safe_title or 'strategy-document'}.pdf"

        doc = SimpleDocTemplate(
            str(path),
            pagesize=LETTER,
            rightMargin=0.65 * inch,
            leftMargin=0.65 * inch,
            topMargin=0.65 * inch,
            bottomMargin=0.65 * inch,
        )
        styles = getSampleStyleSheet()
        heading = ParagraphStyle("LaraloopHeading", parent=styles["Heading2"], textColor=colors.HexColor("#111827"), spaceBefore=10)
        body = ParagraphStyle("LaraloopBody", parent=styles["BodyText"], leading=14, spaceAfter=5)
        story = [Paragraph(document.title, styles["Title"]), Spacer(1, 0.12 * inch)]

        self._section(story, heading, body, "Business Profile", [
            ("Overview", document.business_profile.overview),
            ("Products / Services", document.business_profile.products_or_services),
            ("Key Selling Points", document.business_profile.key_selling_points),
            ("Retail / Distribution", document.business_profile.retail_or_distribution),
            ("Target Audience", document.business_profile.target_audience),
            ("Founder Story", document.business_profile.founder_story or "Not clearly found on the scraped page."),
            ("Marketing Goals", document.business_profile.marketing_goals),
            ("Website", document.business_profile.website),
        ])
        self._section(story, heading, body, "Social Media Strategy", [
            ("Priority Platforms", [f"{plan.priority}. {plan.platform}: {plan.role} Cadence: {plan.posting_cadence}" for plan in document.social_strategy.priority_platforms]),
            ("Content Pillars", document.social_strategy.content_pillars),
            ("Messaging Hierarchy", document.social_strategy.messaging_hierarchy),
            ("Quick Wins", document.social_strategy.quick_wins),
        ])
        self._section(story, heading, body, "Market Research", [
            ("Market Opportunity", document.market_research.market_opportunity),
            ("Trend Tailwinds", document.market_research.trend_tailwinds),
            ("Competitive Landscape", document.market_research.competitive_landscape),
            ("Key Risks", document.market_research.key_risks),
            ("Social Platform Insights", document.market_research.social_platform_insights),
            ("Target Audiences on Social", document.market_research.target_audiences_on_social),
        ])
        self._section(story, heading, body, "Brand Guidelines", [
            ("Brand Personality", document.brand_guidelines.brand_personality),
            ("Colour Palette", [f"{role}: {hex_value}" for role, hex_value in document.brand_guidelines.color_palette.items()]),
            ("Typography", [f"{role}: {font}" for role, font in document.brand_guidelines.typography.items()]),
            ("Design Style", document.brand_guidelines.design_style),
            ("Logo", document.brand_guidelines.logo_url or "No logo candidate found."),
            ("Social Content Principles", document.brand_guidelines.social_content_principles),
        ])
        self._assets(story, heading, body, document)

        doc.build(story)
        return path

    def _section(self, story: list, heading: ParagraphStyle, body: ParagraphStyle, title: str, rows: list[tuple[str, str | list[str]]]) -> None:
        story.append(Paragraph(title, heading))
        for label, value in rows:
            story.append(Paragraph(f"<b>{label}</b>", body))
            if isinstance(value, list):
                for item in value:
                    story.append(Paragraph(f"- {self._escape(item)}", body))
            else:
                story.append(Paragraph(self._escape(value), body))
        story.append(Spacer(1, 0.08 * inch))

    def _assets(self, story: list, heading: ParagraphStyle, body: ParagraphStyle, document: StrategyDocument) -> None:
        story.append(Paragraph("Extracted Website Assets", heading))
        if not document.extracted_assets:
            story.append(Paragraph("No usable assets were extracted from the website.", body))
            return

        rows = [["Type", "Asset", "Notes"]]
        for asset in document.extracted_assets[:30]:
            asset_label = "\n".join(wrap(asset.url, width=48))
            notes = asset.notes or asset.alt or ""
            rows.append([asset.type, asset_label, notes])

        table = Table(rows, colWidths=[0.8 * inch, 4.0 * inch, 2.0 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(table)

    def _escape(self, value: str) -> str:
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
