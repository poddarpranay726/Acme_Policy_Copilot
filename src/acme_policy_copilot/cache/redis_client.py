import os
import redis
from pathlib import Path
from dotenv import load_dotenv

# Locate the project-root .env file
ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError("REDIS_URL is missing from .env")

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    health_check_interval=30,
)

def check_redis_connection():
    return redis_client.ping()


if __name__ == "__main__":
    print("Redis connection:", check_redis_connection())