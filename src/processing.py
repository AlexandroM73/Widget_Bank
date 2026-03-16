from datetime import datetime
from typing import List, Dict, Any


def filter_by_state(data: List[Dict[str, Any]], state: str = 'EXECUTED') -> List[Dict[str, Any]]:
    """
    Фильтрует список словарей по значению ключа 'state'.

    Args:
        data: список словарей, содержащих ключ 'state'
        state: значение ключа 'state' для фильтрации (по умолчанию 'EXECUTED')

    Returns:
        Новый список словарей, где значение ключа 'state' соответствует указанному
    """
    if not isinstance(data, list):
        raise TypeError("Data must be a list")

    return [item for item in data if item.get('state') == state]


def sort_by_date(data: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список словарей по дате (ключ 'date').

    Args:
        data: список словарей, содержащих ключ 'date' в формате ISO
        reverse: порядок сортировки — True для убывания, False для возрастания

    Returns:
        Новый отсортированный список словарей

    Raises:
        ValueError: если дата в некорректном формате
        KeyError: если отсутствует ключ 'date'
    """
    if not isinstance(data, list):
        raise TypeError("Data must be a list")

    def parse_date(item: Dict[str, Any]) -> datetime:
        """Безопасное преобразование строки даты в datetime."""
        if 'date' not in item:
            raise KeyError(f"Missing 'date' key in item: {item}")
        try:
            return datetime.fromisoformat(item['date'])
        except ValueError as e:
            raise ValueError(f"Invalid date format: {item['date']}") from e

    try:
        return sorted(data, key=parse_date, reverse=reverse)
    except (KeyError, ValueError):
        # Если какая‑то дата некорректна, пропускаем её
        valid_items = []
        for item in data:
            try:
                parse_date(item)  # проверяем, что дата корректна
                valid_items.append(item)
            except (KeyError, ValueError):
                continue
        return sorted(valid_items, key=parse_date, reverse=reverse)
