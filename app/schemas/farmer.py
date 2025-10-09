from typing import Optional
from sqlmodel import SQLModel

class FarmerBase(SQLModel):
    name: str
    email: str

class FarmerCreate(FarmerBase):
    password: str

class FarmerRead(FarmerBase):
    id: int

class Farmer(FarmerBase):
    id: int

    class Config:
        orm_mode = True
