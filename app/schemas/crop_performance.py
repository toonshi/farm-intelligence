from typing import Optional
from sqlmodel import SQLModel

class CropPerformanceSchema(SQLModel):
    crop_type: str
    crop_variety: Optional[str] = None
    market_price: Optional[str] = None
    avg_roi: Optional[str] = None
    investment_volume: Optional[str] = None
    risk_level: Optional[str] = None