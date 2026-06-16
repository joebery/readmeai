import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Analysis, AnalysisStatus, Repo
from app.schemas import (
    AnalysisCreate,
    AnalysisResponse,
    EstimateRequest,
    EstimateResponse,
    PushRequest,
    RegenerateRequest,
)
from app.services.file_reader import fetch_repo_files
from app.services.github import GitHubClient
from app.services.readme import push_readme_to_github, run_initial_pipeline
from app.services.tokenizer import STYLE_PRESETS, build_prompt, count_tokens, estimate_cost

router = APIRouter(prefix="/api/v1/analyses", tags=["analyses"])

#Parser for GitHub repo URLs
def parse_repo_url(url: str) -> tuple[str, str]:
    clean = url.strip().rstrip("/").removesuffix(".git")
    #clean example value: github.com/joebery/readmeai
    parts = clean.split("github.com/")
    #parts example value: ['', 'joebery/readmeai']
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    segments = parts[1].split("/")
    #segments example value: ['joebery', 'readmeai']
    if len(segments) < 2:
        raise HTTPException(status_code=400, detail="URL must include owner and repo name")
    return segments[0], segments[1]



async def _run_pipeline(
    analysis_id: uuid.UUID,
    owner: str,
    name: str,
    github_token: str,
    openai_key: str,
    style_prompt: str | None = None, #None = None are optional
    feedback: str | None = None, # These may not always be provided
    existing_readme: str | None = None, # so they are set to None by default
) -> None: # means this function does not return anything
    
    from app.database import AsyncSessionLocal #Importing AsyncSessionLocal here 
    # as a new one is required for each background task to avoid session conflicts



    #PHASE 1: FIND THE ANALYSIS
    #Looks up the analysis record in the database to make sure it exists before proceeding.
    #--------------------------------------------------------------------------------------
    async with AsyncSessionLocal() as db: 
        try:
            result = await db.execute( 
                select(Analysis).where(Analysis.id == analysis_id) 
            )
            analysis = result.scalar_one_or_none()
            if not analysis:
                return
     
    #PHASE 2: UPDATE STATUS TO GENERATING
    #Tells the database the pipeline has started so the fronend spinner changes
    #--------------------------------------------------------------------------------------
            analysis.status = AnalysisStatus.generating
            await db.commit()

    #PHASE 3: RUN THE PIPELINE
    #Calls the readme.py service to fetch files, calls OpenAI, returns README
    #--------------------------------------------------------------------------------------
            output = await run_initial_pipeline(
                owner=owner,
                name=name,
                github_token=github_token,
                openai_key=openai_key,
                style_prompt=style_prompt,
                feedback=feedback,
                existing_readme=existing_readme,
            )
    #PHASE 4: SAVES THE RESULT
    #Saves the generated README to the database and changes status to confirming so the 
    # frontend can show the preview
    #--------------------------------------------------------------------------------------

            analysis.status = AnalysisStatus.confirming
            analysis.readme_content = output["readme_content"]
            analysis.previous_readme = output.get("existing_readme", "")
            analysis.default_branch = output["default_branch"]
            await db.commit()

    #PHASE 5: ERROR HANDLING
    #If anythng goes wrong in phases 1-4, catches the error and saves it to the database
    #  so the frontend can show it
    #--------------------------------------------------------------------------------------
    
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

    # Resolve style
    style_prompt = None
    if body.style and body.style in STYLE_PRESETS:
        style_prompt = STYLE_PRESETS[body.style]
    elif body.style_url:
        try:
            style_readme = await client.get_file_content(
                *parse_repo_url(body.style_url), "README.md"
            )
            if style_readme:
                style_prompt = f"""Analyse and match the style of this README exactly:
- Tone, structure, section order, emoji usage, badge style
{style_readme[:3000]}"""
        except Exception:
            pass

    prompt = build_prompt(metadata, files, style_prompt=style_prompt)
    input_tokens = count_tokens(prompt)
    output_tokens = 2000
    cost = estimate_cost(input_tokens)

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

    analysis = Analysis(
        repo_id=repo.id,
        status=AnalysisStatus.confirming,
        mode="initial",
        style=body.style,
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
    result = await db.execute(
        select(Analysis).where(Analysis.id == body.analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if analysis.status not in (AnalysisStatus.confirming, AnalysisStatus.failed):
        raise HTTPException(
            status_code=409,
            detail=f"Analysis is already in state: {analysis.status}"
        )

    repo_result = await db.execute(
        select(Repo).where(Repo.id == analysis.repo_id)
    )
    repo = repo_result.scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Resolve style prompt
    style_prompt = None
    if body.style and body.style in STYLE_PRESETS:
        style_prompt = STYLE_PRESETS[body.style]
    elif body.style_url:
        try:
            client = GitHubClient(token=body.github_token)
            style_readme = await client.get_file_content(
                *parse_repo_url(body.style_url), "README.md"
            )
            if style_readme:
                style_prompt = f"""Analyse and match the style of this README exactly:
{style_readme[:3000]}"""
        except Exception:
            pass

    analysis.status = AnalysisStatus.queued
    await db.commit()
    await db.refresh(analysis)

    background_tasks.add_task(
        _run_pipeline,
        analysis_id=analysis.id,
        owner=repo.owner,
        name=repo.name,
        github_token=body.github_token,
        openai_key=body.openai_key,
        style_prompt=style_prompt,
    )

    return analysis


@router.post("/{analysis_id}/push", response_model=AnalysisResponse)
async def push_to_github(
    analysis_id: uuid.UUID,
    body: PushRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if analysis.status != AnalysisStatus.confirming:
        raise HTTPException(
            status_code=409,
            detail=f"Analysis is in state {analysis.status} — must be confirming to push"
        )

    if not analysis.readme_content:
        raise HTTPException(status_code=400, detail="No README content to push")

    repo_result = await db.execute(
        select(Repo).where(Repo.id == analysis.repo_id)
    )
    repo = repo_result.scalar_one_or_none()

    analysis.status = AnalysisStatus.pushing
    await db.commit()

    try:
        push_result = await push_readme_to_github(
            owner=repo.owner,
            name=repo.name,
            github_token=body.github_token,
            readme_content=analysis.readme_content,
            branch=analysis.default_branch or "main",
        )
        analysis.status = AnalysisStatus.complete
        analysis.commit_sha = push_result["commit_sha"]
        analysis.commit_url = push_result["commit_url"]
        await db.commit()
        await db.refresh(analysis)
        return analysis

    except Exception as e:
        analysis.status = AnalysisStatus.failed
        analysis.error_message = str(e)
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{analysis_id}/regenerate", response_model=AnalysisResponse)
async def regenerate(
    analysis_id: uuid.UUID,
    body: RegenerateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    repo_result = await db.execute(
        select(Repo).where(Repo.id == analysis.repo_id)
    )
    repo = repo_result.scalar_one_or_none()

    # Store current as previous for diff
    analysis.previous_readme = analysis.readme_content
    analysis.status = AnalysisStatus.queued
    await db.commit()
    await db.refresh(analysis)

    style_prompt = None
    if body.style and body.style in STYLE_PRESETS:
        style_prompt = STYLE_PRESETS[body.style]

    background_tasks.add_task(
        _run_pipeline,
        analysis_id=analysis.id,
        owner=repo.owner,
        name=repo.name,
        github_token=body.github_token,
        openai_key=body.openai_key,
        style_prompt=style_prompt,
        feedback=body.feedback,
        existing_readme=analysis.previous_readme,
    )

    return analysis


@router.delete("/{analysis_id}")
async def discard(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    await db.delete(analysis)
    await db.commit()
    return {"status": "discarded", "analysis_id": str(analysis_id)}


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