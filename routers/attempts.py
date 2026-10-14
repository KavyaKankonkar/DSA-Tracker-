from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Attempt, Problem, User
from schemas import AttemptCreate, AttemptResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.post("/", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED)
async def create_attempt(
    payload: AttemptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Problem).where(Problem.id == payload.problem_id, Problem.user_id == current_user.id)
    )
    problem = result.scalar_one_or_none()
    if problem is None:
        raise HTTPException(404, "Problem not found")

    new_attempt = Attempt(
        problem_id=payload.problem_id,
        time_taken=payload.time_taken,
        status=payload.status,
        notes=payload.notes,
        user_id=current_user.id,
    )
    db.add(new_attempt)
    problem.status = payload.status   # auto-derive: latest attempt wins

    await db.commit()
    await db.refresh(new_attempt)
    return new_attempt


@router.get("/", response_model=list[AttemptResponse])
async def list_attempts(
    problem_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Attempt).where(Attempt.user_id == current_user.id)
    if problem_id is not None:
        query = query.where(Attempt.problem_id == problem_id)
    query = query.order_by(Attempt.attempted_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{attempt_id}", response_model=AttemptResponse)
async def get_attempt(
    attempt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Attempt).where(Attempt.id == attempt_id, Attempt.user_id == current_user.id)
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    return attempt


@router.delete("/{attempt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attempt(
    attempt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Attempt).where(Attempt.id == attempt_id, Attempt.user_id == current_user.id)
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    await db.delete(attempt)
    await db.commit()