from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services.openweather import OpenWeatherError, import_current_weather_for_city

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
