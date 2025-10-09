from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel

class SeasonSchema(SQLModel):
    id: Optional[int] = None
    crop_variety: Optional[str]
    season: Optional[str]
    planted_area_acres: Optional[float]
    yield_kg: Optional[float]
    market_price_kes_per_kg: Optional[float]
    revenue_kes: Optional[float]
    # cost_of_production_kes: Optional[float]
    seed_cost_kes: Optional[float]
    fertilizer_cost_kes: Optional[float]
    pesticide_cost_kes: Optional[float]
    labor_cost_kes: Optional[float]
    machinery_cost_kes: Optional[float]
    other_costs_kes: Optional[float]
    profit_kes: Optional[float]
    planting_date: Optional[datetime]
    harvest_date: Optional[datetime]
    soil_type: Optional[str]
    irrigation_method: Optional[str]
    fertilizer_used: Optional[str]
    pest_control: Optional[str]
    weather_impact: Optional[str]
    notes: Optional[str]
    crop_id: Optional[int] = None
    farm_id: int