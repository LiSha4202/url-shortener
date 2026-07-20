import secrets

# База символов для кодирования Base62
BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode_base62(num: int) -> str:
    """Кодирует число в Base62 строку"""
    if num == 0:
        return BASE62_ALPHABET[0]

    base = len(BASE62_ALPHABET)
    result = []
    while num > 0:
        num, remainder = divmod(num, base)
        result.append(BASE62_ALPHABET[remainder])
    return "".join(reversed(result))


def generaste_short_code(length: int = 6) -> str:
    """Генерирует короткий код через Base62"""
    # Генерируем случайное число
    random_num = secrets.randbelow(62**length)
    code = encode_base62(random_num)

    # Дополняем до нужной длины
    return code.zfill(length)
