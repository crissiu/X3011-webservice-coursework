from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import require_api_key
from app.services.openweather import OpenWeatherError, import_current_weather_for_city

router = APIRouter(prefix="/stations", tags=["stations"])


@router.get("", response_model=list[schemas.StationRead])
def read_stations(db: Session = Depends(get_db)):
    return crud.list_stations(db)


@router.post("", response_model=schemas.StationRead, status_code=status.HTTP_201_CREATED)
def create_station(
    station_in: schemas.StationCreate,
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    if crud.get_station_by_name(db, station_in.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Station name already exists")
    return crud.create_station(db, station_in)


@router.post(
    "/from-openweather",
    response_model=schemas.OpenWeatherImportResult,
    status_code=status.HTTP_201_CREATED,
)
def create_station_from_openweather(
    city: str = Query(..., min_length=2, examples=["York"]),
    db: Session = Depends(get_db),
):
    try:
        return import_current_weather_for_city(db, city)
    except OpenWeatherError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/{station_id}", response_model=schemas.StationDetail)
def read_station(station_id: int, db: Session = Depends(get_db)):
    station = crud.get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    return station


@router.put("/{station_id}", response_model=schemas.StationRead)
def update_station(
    station_id: int,
    station_in: schemas.StationUpdate,
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    station = crud.get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    if station_in.name:
        existing = crud.get_station_by_name(db, station_in.name)
        if existing and existing.id != station_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Station name already exists")
    return crud.update_station(db, station, station_in)


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(
    station_id: int,
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    station = crud.get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    crud.delete_station(db, station)
