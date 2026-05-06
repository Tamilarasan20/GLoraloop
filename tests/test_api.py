from fastapi.testclient import TestClient

from app.db import SessionLocal, init_db
from app.main import app
from app.repositories import JobRepository


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_job_polling_endpoint_returns_created_job() -> None:
    init_db()
    db = SessionLocal()
    try:
        job = JobRepository(db).create("https://example.com/")
    finally:
        db.close()

    client = TestClient(app)
    response = client.get(f"/v1/jobs/{job.id}")

    assert response.status_code == 200
    assert response.json()["id"] == job.id
    assert response.json()["status"] == "queued"
