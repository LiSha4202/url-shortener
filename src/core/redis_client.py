import redis.asyncio as redis

from core.config import settings

redis_client = redis.from_url(
    settings.rds.redis_url,
    decode_responses=True,
)
