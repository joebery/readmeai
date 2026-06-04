from app.services.file_reader import fetch_repo_files
from app.services.github import GitHubClient
from app.services.openai_client import generate_readme
from app.services.tokenizer import build_prompt


async def run_initial_pipeline(
    owner: str,
    name: str,
    github_token: str,
    openai_key: str,
    branch: str = "main",
) -> dict:
    client = GitHubClient(token=github_token)

    # 1. Fetch metadata
    metadata = await client.get_repo_metadata(owner, name)
    branch = metadata["default_branch"]

    # 2. Fetch all files
    files, total_count = await fetch_repo_files(
        client=client,
        owner=owner,
        name=name,
        branch=branch,
    )

    # 3. Check for existing README sha so we can overwrite not duplicate
    existing_sha = None
    existing_content = await client.get_file_content(owner, name, "README.md")
    if existing_content is not None:
        import httpx
        async with httpx.AsyncClient() as http:
            r = await http.get(
                f"https://api.github.com/repos/{owner}/{name}/contents/README.md",
                headers={
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if r.is_success:
                existing_sha = r.json().get("sha")

    # 4. Build prompt and generate README
    prompt = build_prompt(metadata, files)
    readme_content = await generate_readme(prompt, openai_key)

    # 5. Push to GitHub
    result = await client.push_readme(
        owner=owner,
        name=name,
        content=readme_content,
        branch=branch,
        existing_sha=existing_sha,
    )

    commit_sha = result.get("commit", {}).get("sha", "")
    commit_url = result.get("commit", {}).get("html_url", "")

    return {
        "readme_content": readme_content,
        "commit_sha": commit_sha,
        "commit_url": commit_url,
        "file_count": total_count,
        "filtered_file_count": len(files),
    }