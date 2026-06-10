import tiktoken

from app.config import settings
from app.services.file_reader import RepoFile

ENCODING = tiktoken.encoding_for_model("gpt-4o-mini")

STYLE_PRESETS = {
    "minimal": """Style: Minimal and clean. No emojis. Short sentences. 
Brief sections. Gets to the point immediately. Inspired by sindresorhus.""",

    "professional": """Style: Professional and detailed. Use badges extensively. 
Include tables. Formal tone. Comprehensive sections. 
Inspired by microsoft/vscode.""",

    "opensource": """Style: Open source community focused. Welcoming tone. 
Heavy emphasis on contributing section. Include code of conduct mention. 
Inspired by facebook/react.""",

    "portfolio": """Style: Portfolio focused for job seekers. Highlight technical 
decisions and architecture choices. Mention specific skills used. 
Personal but professional tone.""",

    "startup": """Style: Startup/product focused. Marketing language. 
Lead with value proposition. Features first. Energetic tone. 
Inspired by vercel/next.js.""",
}


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def build_file_tree(files: list[RepoFile]) -> str:
    tree = {}
    for f in files:
        parts = f.path.split("/")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = None

    def render(node: dict, prefix: str = "") -> list[str]:
        lines = []
        items = sorted(node.items(), key=lambda x: (x[1] is None, x[0]))
        for i, (name, children) in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            lines.append(f"{prefix}{connector}{name}")
            if children is not None:
                extension = "    " if i == len(items) - 1 else "│   "
                lines.extend(render(children, prefix + extension))
        return lines

    return ".\n" + "\n".join(render(tree))


def build_prompt(
    metadata: dict,
    files: list[RepoFile],
    commits: list[dict] | None = None,
    style_prompt: str | None = None,
    feedback: str | None = None,
    existing_readme: str | None = None,
) -> str:
    files_str = "\n\n".join(
        f"### {f.path}\n```\n{f.content}\n```"
        for f in files
    )

    file_tree = build_file_tree(files)

    commits_str = "No commits found."
    if commits:
        commits_str = "\n".join(
            f"- `{c['sha']}` {c['date']} — {c['message']} ({c['author']})"
            for c in commits
        )

    style_str = ""
    if style_prompt:
        style_str = f"\nSTYLE INSTRUCTIONS:\n{style_prompt}\n"

    feedback_str = ""
    if feedback:
        feedback_str = f"""
USER FEEDBACK ON PREVIOUS VERSION:
The user reviewed the README and requested these changes:
{feedback}
Please apply this feedback in the new version.
"""

    existing_str = ""
    if existing_readme:
        existing_str = f"""
PREVIOUS README VERSION (for reference and diff):
{existing_readme[:3000]}
"""

    return f"""You are an expert technical writer. Generate a complete, professional README.md.

Repository: {metadata['full_name']}
Description: {metadata.get('description') or 'N/A'}
Language: {metadata.get('language') or 'N/A'}
Stars: {metadata.get('stars', 0)}
License: {metadata.get('license_name') or 'not specified'}
Topics: {metadata.get('topics') or 'none'}
{style_str}
{feedback_str}
{existing_str}

Project structure:
{file_tree}

Recent commits:
{commits_str}

Files:
{files_str}

Rules:
- Output ONLY raw markdown, no code fences around the entire output
- Include these sections in order:
  1. Title with shields.io badges for language and license
  2. Description
  3. Features
  4. Tech Stack table
  5. Project Structure — use the file tree provided above, formatted as a code block
  6. Installation — prerequisites, clone, configure, run
  7. Usage — real examples with actual commands
  8. Recent Updates — use the commits above, plain English summary
  9. Contributing
  10. License
- Be specific to THIS project, no generic placeholders
- Never remove existing image references
- Use proper UTF-8 characters for the file tree (├── └── │)"""


def estimate_cost(input_tokens: int) -> float:
    output_tokens = settings.openai_estimated_output_tokens
    input_cost = (input_tokens / 1_000_000) * settings.openai_input_cost_per_1m
    output_cost = (output_tokens / 1_000_000) * settings.openai_output_cost_per_1m
    return round(input_cost + output_cost, 6)