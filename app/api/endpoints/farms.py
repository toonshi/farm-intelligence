from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_async_session
from app.models.models import Farm, Season
from app.schemas.farm import FarmCreate, FarmRead
from app.services.valuation import calculate_simple_valuation, calculate_dcf_valuation
from app.services.recommendation import get_crop_recommendations, get_advanced_recommendations

router = APIRouter()

@router.post("/", response_model=FarmRead)
async def create_farm(*, session: Session = Depends(get_async_session), farm: FarmCreate):
    db_farm = Farm.from_orm(farm)
    session.add(db_farm)
    await session.commit()
    await session.refresh(db_farm)
    return db_farm

@router.get("/{farm_id}/valuation")
async def get_farm_valuation(
    *, session: Session = Depends(get_async_session), farm_id: int
):
    """
    Calculate the valuation of a farm.
    """
    farm = await session.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    result = await session.exec(select(Season).where(Season.farm_id == farm_id))
    seasons = result.all()

    valuation = calculate_simple_valuation(seasons)

    return {"farm_id": farm_id, "valuation": valuation}

@router.get("/{farm_id}/dcf_valuation")
async def get_dcf_farm_valuation(
    *, 
    session: Session = Depends(get_async_session), 
    farm_id: int,
    discount_rate: float = 0.1,
    projection_years: int = 5,
    perpetuity_growth_rate: float = 0.02
):
    """
    Calculate the DCF valuation of a farm.
    """
    farm = await session.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    result = await session.exec(select(Season).where(Season.farm_id == farm_id))
    seasons = result.all()

    valuation = calculate_dcf_valuation(seasons, discount_rate, projection_years, perpetuity_growth_rate)

    return {"farm_id": farm_id, "dcf_valuation": valuation}

from sqlalchemy.orm import selectinload

@router.get("/{farm_id}/recommendations")
async def get_farm_recommendations(
    *, session: Session = Depends(get_async_session), farm_id: int
):
    """
    Get crop recommendations for a farm.
    """
    farm = await session.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    result = await session.exec(
        select(Season).where(Season.farm_id == farm_id).options(selectinload(Season.crop))
    )
    seasons = result.all()

    recommendations = get_crop_recommendations(seasons)

    return {"farm_id": farm_id, "recommendations": recommendations}

@router.get("/{farm_id}/advanced_recommendations")
async def get_advanced_farm_recommendations(
    *, session: Session = Depends(get_async_session), farm_id: int
):
    """
    Get advanced crop recommendations for a farm based on risk-adjusted return.
    """
    farm = await session.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    result = await session.exec(
        select(Season).where(Season.farm_id == farm_id).options(selectinload(Season.crop))
    )
    seasons = result.all()

    recommendations = get_advanced_recommendations(seasons)

    return {"farm_id": farm_id, "recommendations": recommendations}
