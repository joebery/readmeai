import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Repo
from app.schemas import RepoLocksUpdate, RepoResponse

router = APIRouter(prefix="/api/v1/repos", tags=["repos"])


@router.get("/{repo_id}", response_model=RepoResponse)
async def get_repo(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    return repo


@router.patch("/{repo_id}/locks", response_model=RepoResponse)
async def update_locked_sections(
    repo_id: uuid.UUID,
    body: RepoLocksUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    repo.locked_sections = ",".join(body.locked_sections)
    await db.commit()
    await db.refresh(repo)
    return repo