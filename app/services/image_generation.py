from app.config import settings
from app.schemas.brand_kit import BrandKit


class ImageGenerationService:
    async def generate_background(self, brand_kit: BrandKit, prompt: str | None = None) -> str | None:
        if not settings.fal_api_key:
            return None

        # Provider integration placeholder. The service boundary is intentionally real
        # so Fal/Replicate/OpenAI image generation can be wired without changing routes.
        raise NotImplementedError("Fal.ai image generation is configured but not implemented yet.")


class ProductCutoutService:
    async def remove_background(self, image_url: str) -> str:
        if settings.photoroom_api_key:
            raise NotImplementedError("Photoroom cutout integration is configured but not implemented yet.")
        if settings.remove_bg_api_key:
            raise NotImplementedError("remove.bg cutout integration is configured but not implemented yet.")
        return image_url
