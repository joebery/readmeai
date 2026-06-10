import base64
from typing import Any

import httpx


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def get_languages(self, owner: str, name: str) -> list[str]:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}/languages",
                headers=self.headers,
            )
            if not r.is_success:
                return []
            return list(r.json().keys())

    async def get_repo_metadata(self, owner: str, name: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}",
                headers=self.headers,
            )
            r.raise_for_status()
            data = r.json()

        async with httpx.AsyncClient() as client:
            t = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}/topics",
                headers={
                    **self.headers,
                    "Accept": "application/vnd.github.mercy-preview+json",
                },
            )
            topics = t.json().get("names", []) if t.is_success else []

        return {
            "owner": owner,
            "name": name,
            "full_name": data["full_name"],
            "description": data.get("description"),
            "language": data.get("language"),
            "stars": data.get("stargazers_count", 0),
            "license_name": (data.get("license") or {}).get("name"),
            "topics": ",".join(topics),
            "default_branch": data.get("default_branch", "main"),
        }

    async def get_file_tree(self, owner: str, name: str, branch: str = "main") -> list[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}/git/trees/{branch}?recursive=1",
                headers=self.headers,
            )
            r.raise_for_status()
            data = r.json()

        return [
            item for item in data.get("tree", [])
            if item["type"] == "blob"
        ]

    async def get_file_content(self, owner: str, name: str, path: str) -> str | None:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}/contents/{path}",
                headers=self.headers,
            )
            if not r.is_success:
                return None
            data = r.json()

        if data.get("encoding") != "base64":
            return None

        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return None

    async def get_recent_commits(self, owner: str, name: str, limit: int = 10) -> list[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}/commits?per_page={limit}",
                headers=self.headers,
            )
            if not r.is_success:
                return []
            return [
                {
                    "sha": c["sha"][:7],
                    "message": c["commit"]["message"].split("\n")[0],
                    "author": c["commit"]["author"]["name"],
                    "date": c["commit"]["author"]["date"][:10],
                }
                for c in r.json()
            ]

    async def get_push_range_commits(
        self, owner: str, name: str, before_sha: str | None, after_sha: str
    ) -> list[dict]:
        if before_sha is None:
            commits = await self.get_recent_commits(owner, name, limit=1)
            return commits

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}/compare/{before_sha}...{after_sha}",
                headers=self.headers,
            )
            if not r.is_success:
                return []
            data = r.json()

        return [
            {
                "sha": c["sha"][:7],
                "message": c["commit"]["message"].split("\n")[0],
                "author": c["commit"]["author"]["name"],
                "date": c["commit"]["author"]["date"][:10],
            }
            for c in data.get("commits", [])
            if "[bot]" not in c["commit"]["author"]["name"].lower()
            and "readmeai" not in c["commit"]["message"].lower()
        ]

    async def get_changed_files_for_commits(
        self, owner: str, name: str, commits: list[dict]
    ) -> list[str]:
        changed = set()
        async with httpx.AsyncClient() as client:
            for commit in commits:
                r = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{name}/commits/{commit['sha']}",
                    headers=self.headers,
                )
                if not r.is_success:
                    continue
                for f in r.json().get("files", []):
                    if f["status"] != "removed":
                        changed.add(f["filename"])
        return list(changed)

    async def push_readme(
        self,
        owner: str,
        name: str,
        content: str,
        branch: str = "main",
        existing_sha: str | None = None,
    ) -> dict[str, Any]:
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        body: dict[str, Any] = {
            "message": "docs: update README [bot] — ReadmeAI",
            "content": encoded,
            "branch": branch,
        }
        if existing_sha:
            body["sha"] = existing_sha

        async with httpx.AsyncClient() as client:
            r = await client.put(
                f"{self.BASE_URL}/repos/{owner}/{name}/contents/README.md",
                headers=self.headers,
                json=body,
            )
            r.raise_for_status()
            return r.json()