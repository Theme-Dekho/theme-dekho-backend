from google import genai
from google.genai import types
from app.schemas import AIGeneratedWebsite
from app.config import (LLM_PROVIDER, LLM_MODEL, LLM_API_KEY)


def validate_llm_configuration() -> None:
    if not LLM_PROVIDER:
        raise RuntimeError(
            "LLM_PROVIDER is not configured."
        )

    if not LLM_MODEL:
        raise RuntimeError(
            "LLM_MODEL is not configured."
        )

    if not LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is not configured."
        )

def generate_website_content(
    prompt: str,
) -> AIGeneratedWebsite:
    validate_llm_configuration()

    if LLM_PROVIDER != "gemini":
        raise RuntimeError(
            f"Unsupported LLM provider: {LLM_PROVIDER}"
        )

    client = genai.Client(
        api_key=LLM_API_KEY,
    )

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AIGeneratedWebsite,
        ),
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return AIGeneratedWebsite.model_validate_json(
        response.text
    )    