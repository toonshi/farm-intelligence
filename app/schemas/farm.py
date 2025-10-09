from typing import Optional
from sqlmodel import SQLModel

class FarmBase(SQLModel):
    name: str
    county: Optional[str] = None
    location_details: Optional[str] = None

class FarmCreate(FarmBase):
    owner_id: int

class FarmRead(FarmBase):
    id: int
    owner_id: int

class Farm(FarmBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
