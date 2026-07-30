# import os
# import redis
# from dotenv import load_dotenv
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent
# load_dotenv(BASE_DIR / ".env")

# redis_client = redis.from_url(
#     os.getenv("REDIS_URL"),
#     decode_responses=True
# )

import os
import ssl
from pathlib import Path

import redis
from dotenv import load_dotenv
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
import certifi


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

REDIS_URL = os.getenv("REDIS_URL", "").strip()

if not REDIS_URL:
    raise RuntimeError(
        "REDIS_URL is missing from the environment."
    )

if not REDIS_URL.startswith("rediss://"):
    raise RuntimeError(
        "Upstash REDIS_URL must start with rediss://"
    )


redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,

    # Prevent the request from waiting indefinitely.
    socket_connect_timeout=10,
    socket_timeout=10,

    # Detect dead or closed pooled connections.
    health_check_interval=30,
    socket_keepalive=True,

    # Retry temporary connection failures.
    retry=Retry(
        ExponentialBackoff(),
        retries=3,
    ),
    retry_on_error=[
        redis.exceptions.ConnectionError,
        redis.exceptions.TimeoutError,
    ],

    # Verify Upstash TLS certificate.
    # ssl_cert_reqs=ssl.CERT_REQUIRED,
    ssl_cert_reqs=ssl.CERT_REQUIRED,
    ssl_ca_certs=certifi.where(),
)