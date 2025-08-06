from redis import Redis
from rq import Queue

from app.config import get_settings

settings = get_settings()


def get_queue(name: str = "default") -> Queue:
    redis = Redis.from_url(settings.redis_url)
    return Queue(name, connection=redis)
