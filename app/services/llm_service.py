from google import genai
from google.genai import types
from app.schemas import AIGeneratedWebsite
import time
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

    # response = client.models.generate_content(
    #     model=LLM_MODEL,
    #     contents=prompt,
    #     config=types.GenerateContentConfig(
    #         response_mime_type="application/json",
    #         response_schema=AIGeneratedWebsite,
    #     ),
    # )
    response = None

    max_attempts = 4

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=LLM_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AIGeneratedWebsite,
                ),
            )

            break

        except Exception as exc:
            error_text = str(exc)

            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text.lower()
            )

            if (
                not is_temporary_error
                or attempt == max_attempts - 1
            ):
                raise

            wait_seconds = 2 ** attempt

            time.sleep(wait_seconds)

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return AIGeneratedWebsite.model_validate_json(
        response.text
    )    