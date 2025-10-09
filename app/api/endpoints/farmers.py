from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_async_session
from app.models.models import Farmer
from app.schemas.farmer import FarmerCreate, FarmerRead

router = APIRouter()

@router.post("/", response_model=FarmerRead)
async def create_farmer(*, session: Session = Depends(get_async_session), farmer: FarmerCreate):
    db_farmer = Farmer.from_orm(farmer)
    session.add(db_farmer)
    await session.commit()
    await session.refresh(db_farmer)
    return db_farmer
