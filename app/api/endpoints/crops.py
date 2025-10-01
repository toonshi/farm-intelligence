from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_async_session
from app.models.models import Crop

router = APIRouter()

@router.get("/", response_model=List[Crop])
async def read_crops(session: AsyncSession = Depends(get_async_session)):
    result = await session.exec(select(Crop))
    crops = result.all()
    return crops
