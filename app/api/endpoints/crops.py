from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_async_session
from app.models.models import Crop, Season
from app.schemas.crop_performance import CropPerformanceSchema
import math

router = APIRouter()

@router.get("/", response_model=List[Crop])
async def read_crops(session: AsyncSession = Depends(get_async_session)):
    result = await session.exec(select(Crop))
    crops = result.all()
    return crops

@router.get("/performance", response_model=List[CropPerformanceSchema])
async def get_crop_performance(session: AsyncSession = Depends(get_async_session)):
    result = await session.exec(select(Season, Crop).join(Crop))
    season_crop_pairs = result.all()

    crop_data: Dict[str, List[Season]] = {}
    for season, crop in season_crop_pairs:
        if crop.name:
            if crop.name not in crop_data:
                crop_data[crop.name] = []
            crop_data[crop.name].append(season)

    performance_metrics: List[CropPerformanceSchema] = []

    for crop_name, seasons_list in crop_data.items():
        # Filter out seasons with None or NaN values for calculations
        valid_seasons = [
            s for s in seasons_list
            if s.market_price_kes_per_kg is not None and not math.isnan(s.market_price_kes_per_kg)
            and s.profit_kes is not None and not math.isnan(s.profit_kes)
            and s.cost_of_production_kes is not None and not math.isnan(s.cost_of_production_kes)
            and s.revenue_kes is not None and not math.isnan(s.revenue_kes)
        ]

        if not valid_seasons:
            continue

        avg_market_price = sum(s.market_price_kes_per_kg for s in valid_seasons) / len(valid_seasons)

        # Calculate Avg ROI
        total_profit = sum(s.profit_kes for s in valid_seasons)
        total_cost_of_production = sum(s.cost_of_production_kes for s in valid_seasons)
        avg_roi = (total_profit / total_cost_of_production) * 100 if total_cost_of_production else 0

        # Calculate Investment Volume
        investment_volume = sum(s.revenue_kes for s in valid_seasons)

        # Placeholder for Risk Level
        risk_level = "Medium" # Placeholder

        performance_metrics.append(CropPerformanceSchema(
            crop_type=crop_name,
            crop_variety=valid_seasons[0].crop_variety, # Using the crop_variety from the first valid season as a representative
            market_price=f"KSH {avg_market_price:.2f}/kg",
            avg_roi=f"{avg_roi:.2f}%",
            investment_volume=f"KSH {investment_volume/1_000_000:.1f}M",
            risk_level=risk_level
        ))
    return performance_metrics
