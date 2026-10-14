from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_db
from models import Problem, Tag, Pattern, User
from schemas import ProblemCreate, ProblemResponse, ProblemUpdate
from routers.auth import get_current_user

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("/", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    payload: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tags = []
    if payload.tags_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(payload.tags_ids)))
        tags = result.scalars().all()
        if len(tags) != len(payload.tags_ids):
            raise HTTPException(400, "One or more tags_ids are invalid")

    patterns = []
    if payload.pattern_ids:
        result = await db.execute(select(Pattern).where(Pattern.id.in_(payload.pattern_ids)))
        patterns = result.scalars().all()
        if len(patterns) != len(payload.pattern_ids):
            raise HTTPException(400, "One or more pattern_ids are invalid")

    new_problem = Problem(
        problem_name=payload.problem_name,
        description=payload.description,
        user_id=current_user.id,      # never trust this from the body
        tags=tags,
        patterns=patterns,
    )
    db.add(new_problem)
    await db.commit()
    await db.refresh(new_problem)
    return new_problem


@router.get("/", response_model=list[ProblemResponse])
async def list_problems(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Problem)
        .where(Problem.user_id == current_user.id)
        .options(selectinload(Problem.tags), selectinload(Problem.patterns))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Problem)
        .where(Problem.id == problem_id, Problem.user_id == current_user.id)
        .options(selectinload(Problem.tags), selectinload(Problem.patterns))
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(404, "Problem not found")
    return problem


@router.patch("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: int,
    payload: ProblemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Problem)
        .where(Problem.id == problem_id, Problem.user_id == current_user.id)
        .options(selectinload(Problem.tags), selectinload(Problem.patterns))
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(404, "Problem not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "tags_ids" in update_data:
        tag_ids = update_data.pop("tags_ids")
        tag_result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        problem.tags = tag_result.scalars().all()

    if "pattern_ids" in update_data:
        pattern_ids = update_data.pop("pattern_ids")
        pattern_result = await db.execute(select(Pattern).where(Pattern.id.in_(pattern_ids)))
        problem.patterns = pattern_result.scalars().all()

    for field, value in update_data.items():
        setattr(problem, field, value)

    await db.commit()
    await db.refresh(problem)
    return problem


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Problem).where(Problem.id == problem_id, Problem.user_id == current_user.id)
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(404, "Problem not found")
    await db.delete(problem)
    await db.commit()
