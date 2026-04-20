from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/compare", response_model=schemas.CityComparison)
def compare_cities(
    cities: str = Query(
        default="Leeds,Manchester,Birmingham",
        min_length=2,
        description="Comma-separated city list, for example: Leeds,Manchester,Birmingham",
    ),
    data_source: str | None = Query(default=None, pattern="^(demo|openweather)$"),
    db: Session = Depends(get_db),
):
    city_list = [city.strip() for city in cities.split(",") if city.strip()]
    if not city_list:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one city is required")

    comparison = crud.compare_cities(db, city_list, data_source=data_source)
    if comparison.cities_compared == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analytics available for the requested cities",
        )
    return comparison


@router.get("/cities/{city}", response_model=schemas.CityAnalytics)
def city_analytics(
    city: str,
    data_source: str | None = Query(default=None, pattern="^(demo|openweather)$"),
    db: Session = Depends(get_db),
):
    analytics = crud.get_city_analytics(db, city, data_source=data_source)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analytics available for the requested city",
        )
    return analytics


@router.get("/risk-summary", response_model=list[schemas.RiskSummary])
def risk_summary(
    data_source: str | None = Query(default=None, pattern="^(demo|openweather)$"),
    db: Session = Depends(get_db),
):
    return crud.get_latest_risk_summary(db, data_source=data_source)
