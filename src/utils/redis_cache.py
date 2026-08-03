import json
from datetime import datetime, date
from typing import Any, Callable, Awaitable


from core.redis_client import redis_client


def _json_serializer(obj: Any) -> Any:
    """Вспомогательная функция для сериализации сложных типов в JSON"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _json_serializer(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_serializer(i) for i in obj]
    if hasattr(obj, "__dict__"):
        # Если вдруг попался другой объект с __dict__, пробуем преобразовать его словарь
        return _json_serializer(
            {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        )
    return obj


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
        to_store = data

        # Если данные — объект Pydantic/SQLAlchemy, сериализуем в dict
        if hasattr(data, "model_dump"):
            to_store = data.model_dump()
        elif hasattr(data, "__dict__"):
            dict_data = {
                k: v for k, v in data.__dict__.items() if not k.startswith("_")
            }
            to_store = _json_serializer(dict_data)
        else:
            to_store = _json_serializer(data)

        await redis_client.setex(key, ttl, json.dumps(to_store))

    return data
