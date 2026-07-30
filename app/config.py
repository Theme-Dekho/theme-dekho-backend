# from dotenv import load_dotenv
# import os

# load_dotenv()

# ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
# PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
# GRAPH_VERSION = "v25.0"


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



print(
    "WhatsApp token loaded:",
    f"{ACCESS_TOKEN[:8]}...{ACCESS_TOKEN[-4:]}",
)
print("Token loaded:", bool(ACCESS_TOKEN))
print("Token prefix:", ACCESS_TOKEN[:8] if ACCESS_TOKEN else "missing")
print("Token length:", len(ACCESS_TOKEN) if ACCESS_TOKEN else 0)
print("Starts with Bearer:", ACCESS_TOKEN.startswith("Bearer") if ACCESS_TOKEN else False)
print("Phone Number ID:", PHONE_NUMBER_ID)
print("Graph Version:", GRAPH_VERSION)
print("IP hash secret loaded:", bool(IP_HASH_SECRET))