from enum import Enum

from pydantic import BaseModel, HttpUrl

from app.config import settings


class SocialChannel(str, Enum):
    META = "meta"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"


class PublishRequest(BaseModel):
    channel: SocialChannel
    asset_url: HttpUrl
    caption: str


class PublishResult(BaseModel):
    channel: SocialChannel
    status: str
    external_id: str | None = None
    detail: str | None = None


class SocialPublishingService:
    async def publish(self, request: PublishRequest) -> PublishResult:
        token = self._token_for(request.channel)
        if not token:
            return PublishResult(
                channel=request.channel,
                status="not_configured",
                detail=f"{request.channel.value} publishing token is missing.",
            )

        return PublishResult(
            channel=request.channel,
            status="queued",
            detail="Publishing provider adapter is configured but awaits platform-specific account setup.",
        )

    def _token_for(self, channel: SocialChannel) -> str | None:
        if channel == SocialChannel.META:
            return settings.meta_access_token
        if channel == SocialChannel.LINKEDIN:
            return settings.linkedin_access_token
        if channel == SocialChannel.TIKTOK:
            return settings.tiktok_access_token
        return None
