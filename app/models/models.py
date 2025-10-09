from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class Farmer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    farms: List["Farm"] = Relationship(back_populates="owner")

class Farm(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    county: Optional[str]
    location_details: Optional[str]
    owner_id: int = Field(foreign_key="farmer.id")
    owner: Farmer = Relationship(back_populates="farms")
    seasons: List["Season"] = Relationship(back_populates="farm")

class Crop(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    seasons: List["Season"] = Relationship(back_populates="crop")

class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # farmer_name: Optional[str] # Replaced by Farm relationship
    # county: Optional[str] # Moved to Farm model
    crop_variety: Optional[str]
    season: Optional[str] = Field(index=True)
    planted_area_acres: Optional[float]
    yield_kg: Optional[float]
    market_price_kes_per_kg: Optional[float]
    revenue_kes: Optional[float]
    # cost_of_production_kes: Optional[float] # Replaced by detailed costs
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
    # farmer_contact: Optional[str] # Should be part of Farmer model
    notes: Optional[str]
    
    crop_id: Optional[int] = Field(default=None, foreign_key="crop.id")
    farm_id: Optional[int] = Field(default=None, foreign_key="farm.id")

    # Relationships
    crop: Optional[Crop] = Relationship(back_populates="seasons")
    farm: Optional[Farm] = Relationship(back_populates="seasons")
