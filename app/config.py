from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_TOKEN = os.getenv(
    "WHATSAPP_ACCESS_TOKEN",
    "",
).strip()

PHONE_NUMBER_ID = os.getenv(
    "WHATSAPP_PHONE_NUMBER_ID",
    "",
).strip()

GRAPH_VERSION = os.getenv(
    "WHATSAPP_GRAPH_VERSION",
    "v25.0",
).strip()

IP_HASH_SECRET = os.getenv(
    "IP_HASH_SECRET",
    "",
).strip()

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "",
).strip().lower()

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "",
).strip()

LLM_API_KEY = os.getenv(
    "LLM_API_KEY",
    "",
).strip()


if not ACCESS_TOKEN:
    raise RuntimeError(
        "WHATSAPP_ACCESS_TOKEN is missing from the environment."
    )

if not PHONE_NUMBER_ID:
    raise RuntimeError(
        "WHATSAPP_PHONE_NUMBER_ID is missing from the environment."
    )

if not GRAPH_VERSION:
    raise RuntimeError(
        "WHATSAPP_GRAPH_VERSION is missing."
    )

if not IP_HASH_SECRET:
    raise RuntimeError(
        "IP_HASH_SECRET is missing from the environment."
    )

# if not LLM_PROVIDER:
#     raise RuntimeError(
#         "LLM_PROVIDER is missing from the environment."
#     )

# if not LLM_MODEL:
#     raise RuntimeError(
#         "LLM_MODEL is missing from the environment."
#     )

# if not LLM_API_KEY:
#     raise RuntimeError(
#         "LLM_API_KEY is missing from the environment."
#     )

