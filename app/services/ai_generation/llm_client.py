import time
import base64
from pathlib import Path
from typing import Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel

from app.config import (
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_API_KEY,
)


T = TypeVar("T", bound=BaseModel)


def validate_llm_configuration() -> None:
    if not LLM_PROVIDER:
        raise RuntimeError("LLM_PROVIDER is not configured.")

    if not LLM_MODEL:
        raise RuntimeError("LLM_MODEL is not configured.")

    if not LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY is not configured.")


def encode_image_to_data_url(
        image_path: Path,
    ) -> str:
        if not image_path.exists():
            raise FileNotFoundError(
                f"Reference image not found: {image_path}"
            )

        image_bytes = image_path.read_bytes()

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        mime_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }.get(image_path.suffix.lower())

        if not mime_type:
            raise ValueError(
                f"Unsupported reference image type: "
                f"{image_path.suffix}"
            )

        return (
            f"data:{mime_type};base64,"
            f"{encoded_image}"
        )
        


def generate_structured_content(
    prompt: str,
    response_model: Type[T],
    reference_image_path: Path | None = None,
) -> T:
    validate_llm_configuration()

    if LLM_PROVIDER != "openrouter":
        raise RuntimeError(
            f"Unsupported LLM provider: {LLM_PROVIDER}"
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=LLM_API_KEY,
    )

    response = None
    max_attempts = 4

    user_content: list[dict] = [
    {
        "type": "text",
        "text": prompt,
    }
]

    if reference_image_path is not None:
        image_data_url = encode_image_to_data_url(
            reference_image_path
        )

        user_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data_url,
                },
            }
        )

    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return only valid JSON matching "
                            "the requested schema exactly. "
                            "Do not return markdown or explanations."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_content,
                    },
                ],
                response_format={
                    "type": "json_object",
                },
                max_tokens=3500,
                temperature=0,
            )

            break

        except Exception as exc:
            error_text = str(exc)

            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text.lower()
                or "temporarily unavailable" in error_text.lower()
            )

            if (
                not is_temporary_error
                or attempt == max_attempts - 1
            ):
                raise

            time.sleep(2 ** attempt)

    if response is None:
        raise RuntimeError(
            "OpenRouter returned no response."
        )

    if not response.choices:
        raise RuntimeError(
            "OpenRouter returned no choices."
        )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "OpenRouter returned an empty response."
        )

    try:
        return response_model.model_validate_json(content)

    except Exception as exc:
        raise RuntimeError(
            f"Invalid AI generated JSON: {exc}"
        ) from exc