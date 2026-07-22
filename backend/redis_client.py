from redis import Redis
from config import settings

redis = Redis.from_url(
    str(settings.REDIS_URL),
    encoding="utf-8",
    decode_responses=True,
)
