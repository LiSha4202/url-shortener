import json
from typing import Any, Callable, Awaitable
from core.redis_client import redis_client


async def get_or_set_cache(
    key: str,
    fetch_func: Callable[[], Awaitable[Any]],
    ttl: int = 3600,
) -> Any:
    """Универсальная функция для паттерна Cache-Aside"""
    # Пытаемся получить из кеша
    cached = await redis_client.get(key)
    if cached is not None:
        # Если данные — сложный объект, можно хранить JSON
        try:
            return json.loads(cached)
        except (TypeError, json.JSONDecodeError):
            return cached

    # Если нет — вызываем функцию, которая получает данные из БД
    data = await fetch_func()

    # Сохраняем в кеш (если данные не None)
    if data is not None:
        # Если данные — объект Pydantic/SQLAlchemy, сериализуем в dict
        if hasattr(data, "model_dump"):
            to_store = data.model_dump()
        elif hasattr(data, "__dict__"):
            to_store = data.__dict__
        else:
            to_store = data
        await redis_client.setex(key, ttl, json.dumps(to_store))

    return data
