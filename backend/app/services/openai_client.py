from openai import AsyncOpenAI

from app.config import settings


async def generate_readme(prompt: str, api_key: str) -> str:
    client = AsyncOpenAI(api_key=api_key)

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.3,
    )

    content = response.choices[0].message.content

    # Strip markdown code fences if model wraps output in them
    content = content.strip()
    if content.startswith("```markdown"):
        content = content[len("```markdown"):]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]

    return content.strip()