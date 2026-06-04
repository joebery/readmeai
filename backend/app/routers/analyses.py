import uuid
from typing import Any
from app.config import settings

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Analysis, AnalysisStatus, Repo
from app.schemas import (
    AnalysisCreate,
    AnalysisResponse,
    EstimateRequest,
    EstimateResponse,
)
from app.services.file_reader import fetch_repo_files
from app.services.github import GitHubClient
from app.services.readme import run_initial_pipeline
from app.services.tokenizer import build_prompt, count_tokens, estimate_cost

router = APIRouter(prefix="/api/v1/analyses", tags=["analyses"])


def parse_repo_url(url: str) -> tuple[str, str]:
    clean = url.strip().rstrip("/").removesuffix(".git")
    parts = clean.split("github.com/")
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    segments = parts[1].split("/")
    if len(segments) < 2:
        raise HTTPException(status_code=400, detail="URL must include owner and repo name")
    return segments[0], segments[1]


async def _run_pipeline(
    analysis_id: uuid.UUID,
    owner: str,
    name: str,
    github_token: str,
    openai_key: str,
) -> None:
    """Background task — runs the full pipeline and updates the DB."""
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Mark as generating
            result = await db.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            )
            analysis = result.scalar_one_or_none()
            if not analysis:
                return

            analysis.status = AnalysisStatus.generating
            await db.commit()

            # Run the pipeline
            output = await run_initial_pipeline(
                owner=owner,
                name=name,
                github_token=github_token,
                openai_key=openai_key,
            )

            # Mark as pushing
            analysis.status = AnalysisStatus.pushing
            await db.commit()

            # Update with results
            analysis.status = AnalysisStatus.complete
            analysis.readme_content = output["readme_content"]
            analysis.commit_sha = output["commit_sha"]
            analysis.commit_url = output["commit_url"]
            await db.commit()

        except Exception as e:
            async with AsyncSessionLocal() as err_db:
                err_result = await err_db.execute(
                    select(Analysis).where(Analysis.id == analysis_id)
                )
                err_analysis = err_result.scalar_one_or_none()
                if err_analysis:
                    err_analysis.status = AnalysisStatus.failed
                    err_analysis.error_message = str(e)
                    await err_db.commit()


@router.post("/estimate", response_model=EstimateResponse)
async def estimate(
    body: EstimateRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    owner, name = parse_repo_url(body.repo_url)
    client = GitHubClient(token=body.github_token)

    try:
        metadata = await client.get_repo_metadata(owner, name)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"GitHub error: {e}")

    try:
        files, total_count = await fetch_repo_files(
            client=client,
            owner=owner,
            name=name,
            branch=metadata["default_branch"],
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"File fetch error: {e}")

    prompt = build_prompt(metadata, files)
    input_tokens = count_tokens(prompt)
    output_tokens = 2000
    cost = estimate_cost(input_tokens)

    # Upsert repo
    result = await db.execute(
        select(Repo).where(Repo.full_name == metadata["full_name"])
    )
    repo = result.scalar_one_or_none()

    if repo is None:
        repo = Repo(
            owner=owner,
            name=name,
            full_name=metadata["full_name"],
            description=metadata.get("description"),
            language=metadata.get("language"),
            stars=metadata.get("stars", 0),
            license_name=metadata.get("license_name"),
            topics=metadata.get("topics"),
        )
        db.add(repo)
        await db.flush()

    # Create analysis in confirming state
    analysis = Analysis(
        repo_id=repo.id,
        status=AnalysisStatus.confirming,
        mode="initial",
        file_count=total_count,
        filtered_file_count=len(files),
        estimated_input_tokens=input_tokens,
        estimated_output_tokens=output_tokens,
        estimated_cost_usd=str(cost),
    )
    db.add(analysis)
    await db.flush()

    return EstimateResponse(
        repo_full_name=metadata["full_name"],
        file_count=total_count,
        filtered_file_count=len(files),
        estimated_input_tokens=input_tokens,
        estimated_output_tokens=output_tokens,
        estimated_cost_usd=cost,
        model=settings.openai_model,
        analysis_id=analysis.id,
    )


@router.post("", response_model=AnalysisResponse)
async def confirm_and_generate(
    body: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Any:
    # Load the analysis
    result = await db.execute(
        select(Analysis).where(Analysis.id == body.analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found — run estimate first")

    if analysis.status not in (AnalysisStatus.confirming, AnalysisStatus.failed):
        raise HTTPException(
            status_code=409,
            detail=f"Analysis is already in state: {analysis.status}"
        )

    # Load the repo to get owner/name
    repo_result = await db.execute(
        select(Repo).where(Repo.id == analysis.repo_id)
    )
    repo = repo_result.scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Mark as queued
    analysis.status = AnalysisStatus.queued
    await db.commit()
    await db.refresh(analysis)

    # Kick off background task
    background_tasks.add_task(
        _run_pipeline,
        analysis_id=analysis.id,
        owner=repo.owner,
        name=repo.name,
        github_token=body.github_token,
        openai_key=body.openai_key,
    )

    return analysis


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis