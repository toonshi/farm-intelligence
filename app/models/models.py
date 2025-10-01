from typing import List, Optional
from datetime import datetime # Import datetime

from sqlmodel import Field, Relationship, SQLModel


class Crop(SQLModel, table=True): # Define Crop first as Season references it
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    seasons: List["Season"] = Relationship(back_populates="crop", sa_relationship_kwargs={"back_populates": "crop"})


class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    farmer_name: Optional[str]
    county: Optional[str]
    crop_variety: Optional[str]
    season: Optional[str] = Field(index=True) # Renamed from 'name' to 'season'
    planted_area_acres: Optional[float]
    yield_kg: Optional[float]
    market_price_kes_per_kg: Optional[float]
    revenue_kes: Optional[float]
    cost_of_production_kes: Optional[float]
    profit_kes: Optional[float]
    planting_date: Optional[datetime]
    harvest_date: Optional[datetime]
    soil_type: Optional[str]
    irrigation_method: Optional[str]
    fertilizer_used: Optional[str]
    pest_control: Optional[str]
    weather_impact: Optional[str]
    farmer_contact: Optional[str]
    notes: Optional[str]
    crop_id: Optional[int] = Field(default=None, foreign_key="crop.id")

    # Relationship
    crop: Optional[Crop] = Relationship(back_populates="seasons", sa_relationship_kwargs={"back_populates": "seasons"})
