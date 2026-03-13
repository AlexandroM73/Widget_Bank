from datetime import datetime

def filter_by_state(data, state='EXECUTED'):
    """
    Фильтрует список словарей по значению ключа 'state'.

    Args:
        data (list): список словарей, содержащих ключ 'state'
        state (str): значение ключа 'state' для фильтрации (по умолчанию 'EXECUTED')

    Returns:
        list: новый список словарей, где значение ключа 'state' соответствует указанному
    """
    return [item for item in data if item.get('state') == state]



def sort_by_date(data, reverse=True):
    """
    Сортирует список словарей по дате (ключ 'date').

    Args:
        data (list): список словарей, содержащих ключ 'date' в формате ISO (например, '2019-07-03T18:35:29.512364')
        reverse (bool): порядок сортировки — True для убывания (сначала новые), False для возрастания (по умолчанию True)


    Returns:
        list: новый отсортированный список словарей
    """
    def parse_date(item):
        # Преобразуем строку даты в объект datetime для корректного сравнения
        return datetime.fromisoformat(item['date'])

    # Создаём новый отсортированный список, не изменяя исходный
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

    # Проверка с состоянием по умолчанию ('EXECUTED')
    result_default = filter_by_state(test_data)
    print("Результат с состоянием по умолчанию 'EXECUTED':")
    print(result_default)

    # Проверка с указанием состояния 'CANCELED'
    result_canceled = filter_by_state(test_data, 'CANCELED')
    print("\nРезультат с состоянием 'CANCELED':")
    print(result_canceled)

    print("\n=== ТЕСТИРОВАНИЕ ФУНКЦИИ sort_by_date ===")

    # Проверка сортировки по убыванию (по умолчанию)
    result_desc = sort_by_date(test_data)
    print("Результат сортировки по убыванию (сначала самые последние):")
    print(result_desc)

    # Проверка сортировки по возрастанию
    result_asc = sort_by_date(test_data, reverse=False)
    print("\nРезультат сортировки по возрастанию (сначала самые ранние):")
    print(result_asc)

    print("\n=== КОМБИНИРОВАННОЕ ИСПОЛЬЗОВАНИЕ: сначала фильтрация, потом сортировка ===")

    # Сначала фильтруем только 'EXECUTED' операции
    filtered_executed = filter_by_state(test_data, 'EXECUTED')
    # Затем сортируем их по дате (по убыванию)
    sorted_executed_desc = sort_by_date(filtered_executed)
    print("Отфильтрованные 'EXECUTED' и отсортированные по убыванию:")
    print(sorted_executed_desc)
