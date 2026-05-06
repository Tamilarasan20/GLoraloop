from sqlalchemy.orm import Session

from app.models import BrandAnalysisJob, JobStatus, SavedProject, User


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
