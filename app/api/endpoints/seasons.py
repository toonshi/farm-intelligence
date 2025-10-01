from typing import List
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_async_session
from app.models.models import Season
from app.schemas.season import SeasonSchema
import math

router = APIRouter()

@router.get("/", response_model=List[SeasonSchema])
async def read_seasons(
    session: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
):
    result = await session.exec(
        select(Season).offset(skip).limit(limit)
    )
    seasons = result.all()
    processed_seasons = []
    for s in seasons:
        s_dict = s.model_dump()
        for key, value in s_dict.items():
            if isinstance(value, float) and math.isnan(value):
                setattr(s, key, None)
        processed_seasons.append(SeasonSchema.model_validate(s))
    return processed_seasons
