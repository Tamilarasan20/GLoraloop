import re
from pathlib import Path
from urllib.parse import urljoin

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from app.config import settings
from app.schemas.brand_kit import ScrapedBrandData, ScrapedImage


HEX_COLOR_PATTERN = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")
CTA_PATTERN = re.compile(r"\b(shop now|buy now|get started|learn more|book now|contact us|sign up|try now|subscribe)\b", re.I)


class PlaywrightScraper:
    async def scrape(self, url: str) -> ScrapedBrandData:
        settings.artifacts_dir.mkdir(parents=True, exist_ok=True)

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            page = await browser.new_page(viewport={"width": 1440, "height": 1200})

            try:
                response = await page.goto(url, wait_until="networkidle", timeout=settings.scrape_timeout_ms)
                if response and response.status >= 400:
                    raise ValueError(f"Unable to access URL. Received HTTP {response.status}.")

                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(600)
                await page.evaluate("window.scrollTo(0, 0)")

                final_url = page.url
                screenshot_path = self._screenshot_path(final_url)
                await page.screenshot(path=str(screenshot_path), full_page=True)

                extracted = await page.evaluate(
                    """
                    () => {
                      const clean = (value) => (value || '').replace(/\\s+/g, ' ').trim();
                      const text = (selector) => Array.from(document.querySelectorAll(selector))
                        .map((el) => clean(el.innerText || el.textContent))
                        .filter(Boolean);

                      const headings = text('h1, h2, h3').slice(0, 20);
                      const paragraphs = text('p').slice(0, 20);
                      const buttons = text('a, button').slice(0, 80);
                      const metaDescription = document.querySelector('meta[name="description"]')?.content || null;
                      const title = document.title || null;

                      const images = Array.from(document.images).map((img) => {
                        const rect = img.getBoundingClientRect();
                        return {
                          url: img.currentSrc || img.src,
                          alt: img.alt || null,
                          width: img.naturalWidth || Math.round(rect.width) || null,
                          height: img.naturalHeight || Math.round(rect.height) || null,
                          isLogoCandidate: /logo|brand/i.test(`${img.alt || ''} ${img.src || ''}`)
                        };
                      }).filter((img) => img.url).slice(0, 40);

                      const elements = Array.from(document.querySelectorAll('body *')).slice(0, 1500);
                      const colors = [];
                      const fonts = [];
                      for (const el of elements) {
                        const style = window.getComputedStyle(el);
                        colors.push(style.color, style.backgroundColor, style.borderColor);
                        fonts.push(style.fontFamily);
                      }

                      return { title, metaDescription, headings, paragraphs, buttons, images, colors, fonts };
                    }
                    """
                )
            except PlaywrightTimeoutError as exc:
                raise TimeoutError(f"Timed out while scraping {url}.") from exc
            finally:
                await browser.close()

        images = self._normalize_images(url, extracted["images"])
        colors = self._extract_colors(extracted["colors"])
        font_families = self._normalize_fonts(extracted["fonts"])
        headings = self._clean_list(extracted["headings"])
        buttons = self._clean_list(extracted["buttons"])
        ctas = self._extract_ctas(buttons)

        return ScrapedBrandData(
            url=url,
            final_url=final_url,
            title=extracted["title"],
            meta_description=extracted["metaDescription"],
            hero_text=self._hero_text(headings, extracted["paragraphs"]),
            headings=headings,
            ctas=ctas,
            testimonials=self._extract_testimonials(extracted["paragraphs"]),
            colors=colors,
            font_families=font_families,
            logo_url=self._logo_url(images),
            images=images[: settings.max_images],
            screenshot_path=str(screenshot_path),
        )

    def _screenshot_path(self, final_url: str) -> Path:
        safe_name = re.sub(r"[^a-zA-Z0-9]+", "-", final_url).strip("-").lower()[:100]
        return settings.artifacts_dir / f"{safe_name or 'site'}-screenshot.png"

    def _normalize_images(self, base_url: str, raw_images: list[dict]) -> list[ScrapedImage]:
        normalized: list[ScrapedImage] = []
        for image in raw_images:
            width = image.get("width")
            height = image.get("height")
            if width and height and (width < 80 or height < 80):
                continue

            normalized.append(
                ScrapedImage(
                    url=urljoin(base_url, image["url"]),
                    alt=image.get("alt"),
                    width=width,
                    height=height,
                    is_logo_candidate=bool(image.get("isLogoCandidate")),
                )
            )

        return normalized

    def _extract_colors(self, raw_colors: list[str]) -> list[str]:
        counts: dict[str, int] = {}
        for raw in raw_colors:
            if not raw:
                continue

            for color in HEX_COLOR_PATTERN.findall(raw):
                normalized = color.lower()
                counts[normalized] = counts.get(normalized, 0) + 1

            if raw.startswith("rgb"):
                converted = self._rgb_to_hex(raw)
                if converted and converted not in {"#ffffff", "#000000"}:
                    counts[converted] = counts.get(converted, 0) + 1

        return [color for color, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:8]]

    def _rgb_to_hex(self, raw: str) -> str | None:
        values = [int(value) for value in re.findall(r"\d+", raw)[:3]]
        if len(values) != 3:
            return None
        return "#{:02x}{:02x}{:02x}".format(*values)

    def _normalize_fonts(self, raw_fonts: list[str]) -> list[str]:
        seen: set[str] = set()
        fonts: list[str] = []
        for raw in raw_fonts:
            for font in raw.split(","):
                cleaned = font.strip().strip('"').strip("'")
                if cleaned and cleaned not in seen and cleaned.lower() not in {"serif", "sans-serif"}:
                    seen.add(cleaned)
                    fonts.append(cleaned)
        return fonts[:8]

    def _clean_list(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        cleaned: list[str] = []
        for value in values:
            normalized = " ".join(value.split())
            if normalized and normalized not in seen:
                seen.add(normalized)
                cleaned.append(normalized)
        return cleaned

    def _hero_text(self, headings: list[str], paragraphs: list[str]) -> str | None:
        candidates = self._clean_list([*headings[:3], *paragraphs[:3]])
        return " ".join(candidates)[:500] if candidates else None

    def _extract_ctas(self, buttons: list[str]) -> list[str]:
        ctas = [button for button in buttons if CTA_PATTERN.search(button)]
        return self._clean_list(ctas)[:10]

    def _extract_testimonials(self, paragraphs: list[str]) -> list[str]:
        testimonial_markers = ("review", "testimonial", "stars", "loved", "recommend", "customer")
        return [paragraph for paragraph in self._clean_list(paragraphs) if any(marker in paragraph.lower() for marker in testimonial_markers)][:6]

    def _logo_url(self, images: list[ScrapedImage]) -> str | None:
        logo = next((image for image in images if image.is_logo_candidate), None)
        return logo.url if logo else None
