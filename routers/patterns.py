from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Pattern
from schemas import PatternResponse

router = APIRouter(prefix="/patterns", tags=["patterns"])

@router.get("/", response_model=list[PatternResponse])
async def list_patterns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pattern))
    return result.scalars().all()