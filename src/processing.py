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
    return [item for item in data if item.get('state') == state]


def sort_by_date(data: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список словарей по дате (ключ 'date').

    Args:
        data: список словарей, содержащих ключ 'date' в формате ISO
        reverse: порядок сортировки — True для убывания, False для возрастания
    Returns:
        Новый отсортированный список словарей
    """
    def parse_date(item: Dict[str, Any]) -> datetime:
        """Безопасное преобразование строки даты в datetime."""
        return datetime.fromisoformat(item['date'])

    return sorted(data, key=parse_date, reverse=reverse)


# Пример использования и проверки функций
if __name__ == '__main__':
    # Входные данные для проверки
    test_data = [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}
    ]

    print("=== ТЕСТИРОВАНИЕ ФУНКЦИИ filter_by_state ===")
    result_default = filter_by_state(test_data)
    print("Результат с состоянием по умолчанию 'EXECUTED':")
    print(result_default)

    result_canceled = filter_by_state(test_data, 'CANCELED')
    print("\nРезультат с состоянием 'CANCELED':")
    print(result_canceled)

    print("\n=== ТЕСТИРОВАНИЕ ФУНКЦИИ sort_by_date ===")
    result_desc = sort_by_date(test_data)
    print("Результат сортировки по убыванию (сначала самые последние):")
    print(result_desc)

    result_asc = sort_by_date(test_data, reverse=False)
    print("\nРезультат сортировки по возрастанию (сначала самые ранние):")
    print(result_asc)

    print("\n=== КОМБИНИРОВАННОЕ ИСПОЛЬЗОВАНИЕ: сначала фильтрация, потом сортировка ===")
    filtered_executed = filter_by_state(test_data, 'EXECUTED')
    sorted_executed_desc = sort_by_date(filtered_executed)
    print("Отфильтрованные 'EXECUTED' и отсортированные по убыванию:")
    print(sorted_executed_desc)
