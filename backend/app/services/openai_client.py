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

    return response.choices[0].message.content