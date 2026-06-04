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

    async def get_repo_metadata(self, owner: str, name: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}",
                headers=self.headers,
            )
            r.raise_for_status()
            data = r.json()

        # Fetch topics (requires separate accept header)
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
            "message": "docs: generate README with ReadmeAI",
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