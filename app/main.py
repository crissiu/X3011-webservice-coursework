from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import analytics, observations, stations, utility

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A data-driven API for urban climate and air quality monitoring, "
        "combining CRUD operations with analytical endpoints for city-level insights."
    ),
)

app.include_router(stations.router, prefix="/api")
app.include_router(observations.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(utility.router, prefix="/api")


@app.get("/", tags=["root"])
def root():
    return {
        "message": settings.app_name,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }
