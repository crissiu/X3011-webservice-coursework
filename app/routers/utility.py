from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(tags=["utility"])


@router.post("/seed", response_model=schemas.SeedSummary, status_code=status.HTTP_201_CREATED)
def seed_demo_dataset(db: Session = Depends(get_db)):
    return crud.seed_demo_data(db)
