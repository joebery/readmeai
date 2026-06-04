import tiktoken

from app.config import settings
from app.services.file_reader import RepoFile

ENCODING = tiktoken.encoding_for_model("gpt-4o-mini")


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def build_prompt(
    metadata: dict,
    files: list[RepoFile],
) -> str:
    files_str = "\n\n".join(
        f"### {f.path}\n```\n{f.content}\n```"
        for f in files
    )

    return f"""You are an expert technical writer. Generate a complete, professional README.md.

Repository: {metadata['full_name']}
Description: {metadata.get('description') or 'N/A'}
Language: {metadata.get('language') or 'N/A'}
Stars: {metadata.get('stars', 0)}
License: {metadata.get('license_name') or 'not specified'}
Topics: {metadata.get('topics') or 'none'}

Files:
{files_str}

Rules:
- Output ONLY raw markdown
- Include: title with badges, description, features, installation, usage, tech stack, contributing, license
- Use shields.io badges for language and license
- Be specific to THIS project
- Never remove existing image references"""


def estimate_cost(input_tokens: int) -> float:
    output_tokens = settings.openai_estimated_output_tokens
    input_cost = (input_tokens / 1_000_000) * settings.openai_input_cost_per_1m
    output_cost = (output_tokens / 1_000_000) * settings.openai_output_cost_per_1m
    return round(input_cost + output_cost, 6)