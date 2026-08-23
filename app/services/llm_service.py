import time
import base64
from pathlib import Path
from openai import OpenAI
import os
print("LOADED LLM SERVICE:", os.path.abspath(__file__))

from app.config import (
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_API_KEY,
)
from app.schemas import InteriorTemplateGeneratedContent


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

def encode_image_to_base64(
    image_path: str,
) -> str:
    path = Path(image_path)

    if not path.exists():
        raise RuntimeError(
            f"Reference image not found: {image_path}"
        )

    with path.open("rb") as image_file:
        encoded = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    return f"data:image/png;base64,{encoded}"    


def generate_website_content(
    prompt: str,
) -> InteriorTemplateGeneratedContent:
    validate_llm_configuration()

    if LLM_PROVIDER != "openrouter":
        raise RuntimeError(
            f"Unsupported LLM provider: {LLM_PROVIDER}"
        )

    with open("output.txt", "w", encoding="utf-8") as file:
        file.write(prompt)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=LLM_API_KEY,
    )

    response = None
    max_attempts = 4

    for attempt in range(max_attempts):
        try:
            image_data_url = encode_image_to_base64(
                "app/reference_images/interior-reference.png"
            )
            response = client.chat.completions.create(
                model=LLM_MODEL,
             messages=[
                        {
                            "role": "system",
                            "content": (
                                "You generate structured JSON content for a fixed "
                                "Interior & Architecture website template. "
                                "Return ONLY valid JSON matching the user-requested "
                                "schema exactly. "
                                "Do not rename fields. "
                                "Do not return business_name, industry, sub_industry, "
                                "theme, pages, brand_personality, or other old fields. "
                                "Use the exact camelCase fields requested in the prompt. "
                                "Do not return markdown, explanations, or extra fields."
                            ),
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt,
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_data_url,
                                    },
                                },
                            ],
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

            wait_seconds = 2 ** attempt

            time.sleep(wait_seconds)

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
        return InteriorTemplateGeneratedContent.model_validate_json(
            content
        )

    except Exception as exc:
        raise RuntimeError(
            f"Invalid AI website JSON: {exc}"
        ) from exc