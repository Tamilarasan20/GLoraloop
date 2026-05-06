from fastapi import APIRouter

from app.services.social_publishing import PublishRequest, PublishResult, SocialPublishingService


router = APIRouter(prefix="/publishing", tags=["publishing"])


@router.post("/publish", response_model=PublishResult)
async def publish_asset(request: PublishRequest) -> PublishResult:
    return await SocialPublishingService().publish(request)
