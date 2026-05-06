from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import User
from app.repositories import ProjectRepository
from app.schemas.projects import SaveProjectRequest, SavedProjectResponse


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[SavedProjectResponse])
async def list_projects(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SavedProjectResponse]:
    projects = ProjectRepository(db).list_for_user(user.id)
    return [SavedProjectResponse.model_validate(project) for project in projects]


@router.post("", response_model=SavedProjectResponse, status_code=201)
async def save_project(
    request: SaveProjectRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedProjectResponse:
    project = ProjectRepository(db).create(
        user_id=user.id,
        name=request.name,
        source_url=str(request.source_url),
        brand_kit=request.brand_kit.model_dump(mode="json"),
        templates=[template.model_dump(mode="json") for template in request.templates],
    )
    return SavedProjectResponse.model_validate(project)
