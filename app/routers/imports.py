from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services.openweather import (
    OpenWeatherError,
    import_current_weather_for_cities,
    import_current_weather_for_city,
    refresh_current_weather_for_cities,
)

router = APIRouter(prefix="/import", tags=["imports"])


@router.post("/openweather/current", response_model=schemas.OpenWeatherImportResult, status_code=status.HTTP_201_CREATED)
def import_openweather_current(
    city: str = Query(..., min_length=2, examples=["Leeds"]),
    db: Session = Depends(get_db),
):
    try:
        return import_current_weather_for_city(db, city)
    except OpenWeatherError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/openweather/batch",
    response_model=schemas.OpenWeatherBatchImportResult,
    status_code=status.HTTP_201_CREATED,
)
def import_openweather_batch(
    cities: str = Query(
        default="Leeds,Manchester,Birmingham",
        min_length=2,
        description="Comma-separated city list, for example: Leeds,Manchester,Birmingham",
    ),
    db: Session = Depends(get_db),
):
    city_list = [city.strip() for city in cities.split(",") if city.strip()]
    if not city_list:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one city is required")
    try:
        return import_current_weather_for_cities(db, city_list)
    except OpenWeatherError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post(
    "/openweather/refresh",
    response_model=schemas.OpenWeatherBatchImportResult,
    status_code=status.HTTP_201_CREATED,
)
def refresh_openweather_data(
    cities: str = Query(
        default="Leeds,Manchester,Birmingham",
        min_length=2,
        description="Comma-separated city list. Existing OpenWeatherMap data is replaced.",
    ),
    db: Session = Depends(get_db),
):
    city_list = [city.strip() for city in cities.split(",") if city.strip()]
    if not city_list:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one city is required")
    try:
        return refresh_current_weather_for_cities(db, city_list)
    except OpenWeatherError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
