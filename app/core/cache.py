from fastapi import Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as aioredis
from app.core.config import settings


async def init_cache():
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=False)
    FastAPICache.init(RedisBackend(redis), prefix="taller")


def taller_key_builder(func, namespace: str = "", *, request: Request = None, response: Response = None, **kwargs):
    """Cache key que incluye taller_id del JWT para aislar datos entre talleres."""
    taller_id = ""
    if request:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            from jose import jwt
            from app.core.config import settings as s
            try:
                payload = jwt.decode(auth[7:], s.SECRET_KEY, algorithms=[s.ALGORITHM])
                taller_id = payload.get("taller_id", "")
            except Exception:
                pass
    return f"{namespace}:{taller_id}:{func.__module__}:{func.__name__}"


async def invalidate_taller_cache(taller_id: str, namespace: str = ""):
    """Invalida todas las keys de cache de un taller específico."""
    backend = FastAPICache.get_backend()
    prefix = FastAPICache.get_prefix()
    key = f"{prefix}:{namespace}:{taller_id}"
    try:
        redis_client = backend.redis
        pattern = f"{prefix}:*:{taller_id}:*"
        async for k in redis_client.scan_iter(pattern):
            await redis_client.delete(k)
    except Exception:
        pass
