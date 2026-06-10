from app.services.file_reader import fetch_repo_files
from app.services.github import GitHubClient
from app.services.openai_client import generate_readme
from app.services.tokenizer import build_prompt


async def run_initial_pipeline(
    owner: str,
    name: str,
    github_token: str,
    openai_key: str,
    style_prompt: str | None = None,
    feedback: str | None = None,
    existing_readme: str | None = None,
) -> dict:
    """
    Main pipeline for Mode 1 — generates a README from scratch.
    Does NOT push to GitHub. Returns the generated content for the user to review first.
    """
    client = GitHubClient(token=github_token)

    # Step 1 — Fetch repo metadata (name, description, stars, license, topics)
    # and the list of languages used in the repo
    metadata = await client.get_repo_metadata(owner, name)
    branch = metadata["default_branch"]
    languages = await client.get_languages(owner, name)

    # Step 2 — Fetch all files in the repo, filter out binaries and
    # lock files, truncate large files to stay within token limits
    files, total_count = await fetch_repo_files(
        client=client,
        owner=owner,
        name=name,
        branch=branch,
    )

    # Step 3 — Fetch the last 10 commits so the AI can populate
    # the "Recent Updates" section with real commit history
    commits = await client.get_recent_commits(owner, name, limit=10)

    # Step 4 — Fetch the existing README from GitHub if one exists.
    # This is stored as previous_readme in the database so the frontend
    # can show a diff between the old and new versions before the user pushes
    existing_readme_content = await client.get_file_content(owner, name, "README.md")
    print(f"DEBUG existing_readme length: {len(existing_readme_content) if existing_readme_content else 'None'}")

    # Step 5 — Build the prompt with all the context we've gathered,
    # then send it to OpenAI to generate the README content
    prompt = build_prompt(
        metadata=metadata,
        files=files,
        commits=commits,
        style_prompt=style_prompt,   # optional — preset or copied from another repo
        feedback=feedback,            # optional — user's feedback on a previous version
        existing_readme=existing_readme,  # optional — passed in on regenerate
        languages=languages,
    )
    readme_content = await generate_readme(prompt, openai_key)

    # Return everything the router needs to update the analysis record
    # Note: existing_readme_content is what's currently on GitHub —
    # stored as previous_readme so the diff view works on the frontend
    return {
        "readme_content": readme_content,
        "file_count": total_count,
        "filtered_file_count": len(files),
        "default_branch": branch,
        "existing_readme": existing_readme_content or "",
    }


async def push_readme_to_github(
    owner: str,
    name: str,
    github_token: str,
    readme_content: str,
    branch: str = "main",
) -> dict:
    """
    Pushes the generated README to GitHub as a commit.
    Only called after the user has reviewed and approved the preview.
    If a README already exists, fetches its SHA so GitHub knows to overwrite
    it rather than create a duplicate file.
    """
    client = GitHubClient(token=github_token)

    # Check if a README already exists and get its SHA.
    # GitHub requires the SHA to update an existing file —
    # without it the API returns a 422 conflict error
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

    # Push the README to GitHub — the push_readme method in GitHubClient
    # handles the base64 encoding and the PUT request to the contents API
    result = await client.push_readme(
        owner=owner,
        name=name,
        content=readme_content,
        branch=branch,
        existing_sha=existing_sha,
    )

    # Return the commit SHA and URL so we can store them in the database
    # and show the user a link to the commit on GitHub
    return {
        "commit_sha": result.get("commit", {}).get("sha", ""),
        "commit_url": result.get("commit", {}).get("html_url", ""),
    }