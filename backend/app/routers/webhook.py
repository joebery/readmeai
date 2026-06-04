import hashlib
import hmac
import json
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Analysis, AnalysisStatus, Repo
from app.services.update import run_update_pipeline

router = APIRouter(prefix="/api/v1/webhook", tags=["webhook"])


def verify_signature(payload: bytes, secret: str, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def _run_update_background(
    analysis_id,
    owner: str,
    name: str,
    github_token: str,
    openai_key: str,
    locked_sections: list[str] | None,
    before_sha: str | None,
    after_sha: str,
) -> None:
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Analysis).where(Analysis.id == analysis_id)
            )
            analysis = result.scalar_one_or_none()
            if not analysis:
                return

            analysis.status = AnalysisStatus.generating
            await db.commit()

            output = await run_update_pipeline(
                owner=owner,
                name=name,
                github_token=github_token,
                openai_key=openai_key,
                locked_sections=locked_sections,
                before_sha=before_sha,
                after_sha=after_sha,
            )

            if output.get("skipped"):
                analysis.status = AnalysisStatus.complete
                analysis.error_message = f"Skipped: {output['reason']}"
            else:
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


@router.post("/github/{repo_id}")
async def github_webhook(
    repo_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    x_github_event: str = Header(default=""),
    x_hub_signature_256: str = Header(default=""),
    x_github_token: str = Header(default=""),
    x_openai_key: str = Header(default=""),
) -> Any:
    # Debug — print everything received
    print(f"DEBUG EVENT: '{x_github_event}'")
    print(f"DEBUG TOKEN: '{x_github_token}'")
    print(f"DEBUG KEY: '{x_openai_key}'")
    print(f"DEBUG ALL HEADERS: {dict(request.headers)}")
    # Only handle push events
    if x_github_event != "push":
        return {"status": "ignored", "reason": f"event {x_github_event} not handled"}

    # Validate tokens present
    if not x_github_token or not x_openai_key:
        raise HTTPException(
            status_code=400,
            detail="X-GitHub-Token and X-OpenAI-Key headers required"
        )

    print(f"DEBUG token received: '{x_github_token[:10]}...' key: '{x_openai_key[:5]}...'")

    payload = await request.body()
    data = json.loads(payload)

    # Load repo from DB
    result = await db.execute(
        select(Repo).where(Repo.id == repo_id)
    )
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Verify webhook secret if configured
    if repo.webhook_secret and x_hub_signature_256:
        if not verify_signature(payload, repo.webhook_secret, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Bot loop prevention
    pusher = data.get("pusher", {}).get("name", "").lower()
    head_commit_msg = (data.get("head_commit") or {}).get("message", "").lower()

    if "[bot]" in pusher or "readmeai" in pusher:
        return {"status": "ignored", "reason": "bot push detected"}

    if "[bot]" in head_commit_msg or "docs: update readme" in head_commit_msg:
        return {"status": "ignored", "reason": "bot commit detected"}

    # Get push range
    before_sha = data.get("before")
    after_sha = data.get("after")

    if not after_sha:
        return {"status": "ignored", "reason": "no after sha in payload"}

    if before_sha == "0000000000000000000000000000000000000000":
        before_sha = None

    locked_sections = (
        [s.strip() for s in repo.locked_sections.split(",")]
        if repo.locked_sections
        else None
    )

    # Create analysis record
    analysis = Analysis(
        repo_id=repo.id,
        status=AnalysisStatus.queued,
        mode="update",
    )
    db.add(analysis)
    await db.flush()

    # Capture token values before request ends
    github_token = x_github_token
    openai_key = x_openai_key

    background_tasks.add_task(
        _run_update_background,
        analysis_id=analysis.id,
        owner=repo.owner,
        name=repo.name,
        github_token=github_token,
        openai_key=openai_key,
        locked_sections=locked_sections,
        before_sha=before_sha,
        after_sha=after_sha,
    )

    return {
        "status": "queued",
        "analysis_id": str(analysis.id),
    }