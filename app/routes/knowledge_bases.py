from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import User
from app.repositories import KnowledgeBaseRepository
from app.schemas.knowledge_base import (
    BuildKnowledgeBaseRequest,
    KnowledgeBaseResponse,
    KnowledgeDocumentType,
    SaveKnowledgeBaseRequest,
    UpdateKnowledgeDocumentRequest,
)
from app.services.knowledge_base_builder import KnowledgeBaseBuilder
from app.services.pipeline import BrandDnaPipeline


router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


@router.get("", response_model=list[KnowledgeBaseResponse])
async def list_knowledge_bases(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[KnowledgeBaseResponse]:
    records = KnowledgeBaseRepository(db).list_for_user(user.id)
    return [KnowledgeBaseResponse.model_validate(record) for record in records]


@router.get("/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    knowledge_base_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    record = KnowledgeBaseRepository(db).get_for_user(knowledge_base_id, user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return KnowledgeBaseResponse.model_validate(record)


@router.post("", response_model=KnowledgeBaseResponse, status_code=201)
async def save_knowledge_base(
    request: SaveKnowledgeBaseRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    return _save_analysis(str(request.source_url), request.analysis, user, db)


@router.post("/build", response_model=KnowledgeBaseResponse, status_code=201)
async def build_knowledge_base(
    request: BuildKnowledgeBaseRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    analysis = await BrandDnaPipeline().analyze_with_strategy_document(str(request.url))
    return _save_analysis(str(request.url), analysis, user, db)


@router.patch("/{knowledge_base_id}/documents/{document_type}", response_model=KnowledgeBaseResponse)
async def update_knowledge_document(
    knowledge_base_id: str,
    document_type: KnowledgeDocumentType,
    request: UpdateKnowledgeDocumentRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    try:
        record = KnowledgeBaseRepository(db).update_document(
            knowledge_base_id,
            user.id,
            document_type.value,
            request.content,
        )
        return KnowledgeBaseResponse.model_validate(record)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _save_analysis(source_url: str, analysis, user: User, db: Session) -> KnowledgeBaseResponse:
    builder = KnowledgeBaseBuilder()
    business_profile, market_research, social_strategy = builder.documents(analysis)
    record = KnowledgeBaseRepository(db).create(
        user_id=user.id,
        business_name=analysis.brand_kit.brand_name,
        website=source_url,
        scraped_data=analysis.scraped_data.model_dump(mode="json"),
        enriched_data=builder.enriched_data(analysis.brand_kit),
        brand_guidelines=builder.brand_guidelines(analysis),
        brand_memory=builder.brand_memory(analysis),
        visual_assets=builder.visual_assets(analysis),
        business_profile=business_profile,
        market_research=market_research,
        social_strategy=social_strategy,
        strategy_pdf_url=analysis.strategy_pdf_url,
    )
    return KnowledgeBaseResponse.model_validate(record)
