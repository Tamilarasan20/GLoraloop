from fastapi import FastAPI

from app.routes.brand_kits import router as brand_kits_router


app = FastAPI(
    title="Laraloop Brand DNA Extractor",
    version="0.1.0",
    description="Backend for extracting brand context and campaign-ready JSON from a business URL.",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(brand_kits_router, prefix="/v1")
