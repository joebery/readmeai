import asyncio
from dataclasses import dataclass

from app.services.github import GitHubClient

# File extensions we can meaningfully read
READABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".rb", ".php", ".cs", ".cpp", ".c", ".h", ".swift", ".kt",
    ".md", ".txt", ".rst", ".yaml", ".yml", ".toml", ".json",
    ".env.example", ".sh", ".bash", ".zsh", ".fish",
    ".dockerfile", ".sql", ".html", ".css", ".scss",
    ".xml", ".ini", ".cfg", ".conf",
}

# Filenames to always include regardless of extension
ALWAYS_INCLUDE = {
    "dockerfile", "makefile", "procfile", "justfile",
    "requirements.txt", "pipfile", "gemfile", "rakefile",
    "package.json", "package-lock.json", "yarn.lock",
    "cargo.toml", "cargo.lock", "go.mod", "go.sum",
    "pom.xml", "build.gradle", "settings.gradle",
    "pyproject.toml", "setup.py", "setup.cfg",
    ".env.example", "docker-compose.yml", "docker-compose.yaml",
}

# Paths to always skip
SKIP_PATHS = {
    "node_modules", ".git", "__pycache__", ".pytest_cache",
    ".mypy_cache", "dist", "build", ".next", "venv", ".venv",
    "env", ".tox", "coverage", ".nyc_output",
}

# Max characters to read per file (avoids huge files blowing token budget)
MAX_CHARS_PER_FILE = 3000
# Max files to fetch content for
MAX_FILES = 80


@dataclass
class RepoFile:
    path: str
    content: str
    char_count: int


def _should_include(path: str) -> bool:
    parts = path.lower().split("/")

    # Skip if any path segment is in the skip list
    for part in parts:
        if part in SKIP_PATHS:
            return False

    filename = parts[-1]

    # Always include specific filenames
    if filename in ALWAYS_INCLUDE:
        return True

    # Include by extension
    for ext in READABLE_EXTENSIONS:
        if filename.endswith(ext):
            return True

    return False


async def fetch_repo_files(
    client: GitHubClient,
    owner: str,
    name: str,
    branch: str = "main",
) -> tuple[list[RepoFile], int]:
    """
    Returns (files_with_content, total_file_count)
    """
    tree = await client.get_file_tree(owner, name, branch)
    total_count = len(tree)

    # Filter to readable files
    filtered = [item for item in tree if _should_include(item["path"])]

    # Sort: root files first, then by path depth, then alphabetically
    filtered.sort(key=lambda x: (x["path"].count("/"), x["path"]))

    # Cap at MAX_FILES
    filtered = filtered[:MAX_FILES]

    # Fetch all file contents concurrently
    async def fetch(item: dict) -> RepoFile | None:
        content = await client.get_file_content(owner, name, item["path"])
        if content is None:
            return None
        truncated = content[:MAX_CHARS_PER_FILE]
        return RepoFile(
            path=item["path"],
            content=truncated,
            char_count=len(truncated),
        )

    results = await asyncio.gather(*[fetch(item) for item in filtered])
    files = [r for r in results if r is not None]

    return files, total_count