import json
import os
from typing import List, Dict, Any


def read_json_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON‑файл с финансовыми транзакциями.

    Args:
        file_path (str): путь к JSON‑файлу.

    Returns:
        List[Dict[str, Any]]: список словарей с данными о транзакциях;
            пустой список, если файл не найден, пуст или содержит не‑список.
    """
    # Проверяем существование файла
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем, что данные — список
        if isinstance(data, list):
            return data
        else:
            return []

    except (json.JSONDecodeError, UnicodeDecodeError):
        # Файл пуст, повреждён или не в UTF‑8 — возвращаем пустой список
        return []
    except Exception:
        # Любые другие непредвиденные ошибки — возвращаем пустой список
        return []
