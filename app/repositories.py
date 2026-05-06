from sqlalchemy.orm import Session

from app.models import BrandAnalysisJob, JobStatus, KnowledgeBase, SavedProject, User


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, url: str) -> BrandAnalysisJob:
        job = BrandAnalysisJob(url=url)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get(self, job_id: str) -> BrandAnalysisJob | None:
        return self.db.get(BrandAnalysisJob, job_id)

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        stage: str,
        progress: int,
        error: str | None = None,
        result: dict | None = None,
    ) -> BrandAnalysisJob:
        job = self.db.get(BrandAnalysisJob, job_id)
        if job is None:
            raise ValueError(f"Job {job_id} was not found.")

        job.status = status
        job.stage = stage
        job.progress = progress
        job.error = error
        if result is not None:
            job.result = result
        self.db.commit()
        self.db.refresh(job)
        return job


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create(self, email: str, display_name: str | None = None) -> User:
        user = self.db.query(User).filter(User.email == email).one_or_none()
        if user is not None:
            return user

        user = User(email=email, display_name=display_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user_id: str, name: str, source_url: str, brand_kit: dict, templates: list) -> SavedProject:
        project = SavedProject(
            user_id=user_id,
            name=name,
            source_url=source_url,
            brand_kit=brand_kit,
            templates=templates,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def list_for_user(self, user_id: str) -> list[SavedProject]:
        return (
            self.db.query(SavedProject)
            .filter(SavedProject.user_id == user_id)
            .order_by(SavedProject.updated_at.desc())
            .all()
        )


class KnowledgeBaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        user_id: str,
        business_name: str,
        website: str,
        scraped_data: dict,
        enriched_data: dict,
        brand_guidelines: dict,
        brand_memory: dict,
        visual_assets: list,
        business_profile: str,
        market_research: str,
        social_strategy: str,
        strategy_pdf_url: str | None,
    ) -> KnowledgeBase:
        knowledge_base = KnowledgeBase(
            user_id=user_id,
            business_name=business_name,
            website=website,
            scraped_data=scraped_data,
            enriched_data=enriched_data,
            brand_guidelines=brand_guidelines,
            brand_memory=brand_memory,
            visual_assets=visual_assets,
            business_profile=business_profile,
            market_research=market_research,
            social_strategy=social_strategy,
            strategy_pdf_url=strategy_pdf_url,
        )
        self.db.add(knowledge_base)
        self.db.commit()
        self.db.refresh(knowledge_base)
        return knowledge_base

    def list_for_user(self, user_id: str) -> list[KnowledgeBase]:
        return (
            self.db.query(KnowledgeBase)
            .filter(KnowledgeBase.user_id == user_id)
            .order_by(KnowledgeBase.updated_at.desc())
            .all()
        )

    def get_for_user(self, knowledge_base_id: str, user_id: str) -> KnowledgeBase | None:
        return (
            self.db.query(KnowledgeBase)
            .filter(KnowledgeBase.id == knowledge_base_id, KnowledgeBase.user_id == user_id)
            .one_or_none()
        )

    def update_document(self, knowledge_base_id: str, user_id: str, document_type: str, content: str) -> KnowledgeBase:
        knowledge_base = self.get_for_user(knowledge_base_id, user_id)
        if knowledge_base is None:
            raise ValueError("Knowledge base not found")
        if document_type not in {"business_profile", "market_research", "social_strategy"}:
            raise ValueError("Unsupported document type")

        setattr(knowledge_base, document_type, content)
        self.db.commit()
        self.db.refresh(knowledge_base)
        return knowledge_base
