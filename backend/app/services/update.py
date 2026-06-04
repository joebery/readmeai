from app.services.file_reader import RepoFile
from app.services.github import GitHubClient
from app.services.openai_client import generate_readme
from app.services.tokenizer import count_tokens, estimate_cost


BOT_NAMES = {"readmeai", "github-actions[bot]", "dependabot[bot]"}
BOT_MESSAGE_MARKERS = ["[bot]", "docs: update readme", "docs: generate readme"]


def is_bot_commit(message: str, author: str) -> bool:
    msg_lower = message.lower()
    author_lower = author.lower()
    if any(marker in msg_lower for marker in BOT_MESSAGE_MARKERS):
        return True
    if any(bot in author_lower for bot in BOT_NAMES):
        return True
    return False


def build_update_prompt(
    metadata: dict,
    existing_readme: str,
    changed_files: list[RepoFile],
    commits: list[dict],
    locked_sections: list[str] | None = None,
) -> str:
    changed_str = "\n\n".join(
        f"### {f.path}\n```\n{f.content}\n```"
        for f in changed_files
    )

    commits_str = "\n".join(
        f"- `{c['sha']}` {c['date']} — {c['message']} ({c['author']})"
        for c in commits
    )

    locked_str = ""
    if locked_sections:
        locked_str = "\nLOCKED SECTIONS — do not modify these under any circumstances:\n"
        locked_str += "\n".join(f"- {s}" for s in locked_sections)

    return f"""You are an expert technical writer. Update an existing README.md based on recent code changes.

Repository: {metadata['full_name']}
{locked_str}

CRITICAL RULES:
- Make SURGICAL edits only — do not rewrite sections that were not affected by the changes
- NEVER remove existing images, badges, or shields
- NEVER modify locked sections listed above
- Update ONLY sections that are directly affected by the changed files
- Append a new dated entry to the "## Recent Updates" section (create it if absent)
- The Recent Updates entry should be a plain English summary of user-facing changes, not raw commit messages
- Ignore internal refactors, formatting fixes, and bot commits in the summary
- Commit with message containing [bot] to prevent webhook loops
- Output ONLY the full updated README.md in raw markdown

Commits in this push:
{commits_str}

Files changed:
{changed_str or "No file content changes — metadata only"}

Existing README:
{existing_readme}"""


async def run_update_pipeline(
    owner: str,
    name: str,
    github_token: str,
    openai_key: str,
    locked_sections: list[str] | None = None,
    before_sha: str | None = None,
    after_sha: str | None = None,
) -> dict:
    client = GitHubClient(token=github_token)

    # 1. Fetch metadata
    metadata = await client.get_repo_metadata(owner, name)
    branch = metadata["default_branch"]

    # 2. Get commits in push range
    if after_sha:
        commits = await client.get_push_range_commits(owner, name, before_sha, after_sha)
    else:
        commits = await client.get_recent_commits(owner, name, limit=5)

    # Filter out bot commits
    commits = [
        c for c in commits
        if not is_bot_commit(c["message"], c["author"])
    ]

    if not commits:
        return {"skipped": True, "reason": "All commits in push were bot commits"}

    # 3. Get changed files
    changed_paths = await client.get_changed_files_for_commits(owner, name, commits)

    # 4. Fetch content of changed files
    changed_files = []
    for path in changed_paths:
        content = await client.get_file_content(owner, name, path)
        if content:
            changed_files.append(
                RepoFile(path=path, content=content[:2000], char_count=len(content))
            )

    # 5. Fetch existing README
    existing_readme = await client.get_file_content(owner, name, "README.md")
    if not existing_readme:
        return {"skipped": True, "reason": "No existing README — run Mode 1 first"}

    # 6. Get existing README sha for overwrite
    import httpx
    async with httpx.AsyncClient() as http:
        r = await http.get(
            f"https://api.github.com/repos/{owner}/{name}/contents/README.md",
            headers={
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        existing_sha = r.json().get("sha") if r.is_success else None

    # 7. Build prompt and generate
    prompt = build_update_prompt(
        metadata=metadata,
        existing_readme=existing_readme,
        changed_files=changed_files,
        commits=commits,
        locked_sections=locked_sections,
    )
    updated_readme = await generate_readme(prompt, openai_key)

    # 8. Push updated README
    result = await client.push_readme(
        owner=owner,
        name=name,
        content=updated_readme,
        branch=branch,
        existing_sha=existing_sha,
    )

    return {
        "readme_content": updated_readme,
        "commit_sha": result.get("commit", {}).get("sha", ""),
        "commit_url": result.get("commit", {}).get("html_url", ""),
        "commits_processed": len(commits),
        "changed_files": len(changed_files),
        "skipped": False,
    }


def estimate_update_tokens(
    existing_readme: str,
    changed_files: list[RepoFile],
    commits: list[dict],
) -> tuple[int, float]:
    combined = existing_readme + "\n".join(f.content for f in changed_files)
    combined += "\n".join(c["message"] for c in commits)
    tokens = count_tokens(combined)
    cost = estimate_cost(tokens)
    return tokens, cost