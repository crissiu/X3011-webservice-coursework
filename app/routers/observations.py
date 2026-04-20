from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/observations", tags=["observations"])


@router.get("", response_model=list[schemas.ObservationRead])
def read_observations(
    city: str | None = Query(default=None),
    station_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    return crud.list_observations(db, city=city, station_id=station_id)


@router.post("", response_model=schemas.ObservationRead, status_code=status.HTTP_201_CREATED)
def create_observation(observation_in: schemas.ObservationCreate, db: Session = Depends(get_db)):
    station = crud.get_station(db, observation_in.station_id)
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    return crud.create_observation(db, observation_in)


@router.get("/{observation_id}", response_model=schemas.ObservationRead)
def read_observation(observation_id: int, db: Session = Depends(get_db)):
    observation = crud.get_observation(db, observation_id)
    if not observation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")
    return observation


@router.put("/{observation_id}", response_model=schemas.ObservationRead)
def update_observation(
    observation_id: int,
    observation_in: schemas.ObservationUpdate,
    db: Session = Depends(get_db),
):
    observation = crud.get_observation(db, observation_id)
    if not observation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")
    if observation_in.station_id is not None and not crud.get_station(db, observation_in.station_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    return crud.update_observation(db, observation, observation_in)


@router.delete("/{observation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_observation(observation_id: int, db: Session = Depends(get_db)):
    observation = crud.get_observation(db, observation_id)
    if not observation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")
    crud.delete_observation(db, observation)
