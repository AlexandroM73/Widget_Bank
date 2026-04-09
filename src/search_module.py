import re
from typing import List, Dict, Any


def process_bank_search(data: List[Dict[str, Any]], search_string: str) -> List[Dict[str, Any]]:
    """
    Ищет транзакции по ключевому слову или фразе в поле 'description'.

    Функция выполняет поиск с учётом следующих особенностей:
    - регистр не имеет значения (поиск регистронезависимый);
    - специальные символы в строке поиска автоматически экранируются,
      что позволяет искать строки с точками, процентами и т. д.;
    - если строка поиска пустая или состоит только из пробелов, возвращается пустой список;
    - транзакции без поля 'description' или с пустым описанием пропускаются.

    Параметры:
        data (List[Dict[str, Any]]): список транзакций. Каждая транзакция — словарь,
            который может содержать поле 'description' с текстом описания операции.
            Другие поля (например, 'amount', 'date') сохраняются в результате,
            если транзакция соответствует условию поиска.
        search_string (str): строка для поиска в описаниях транзакций.
            Может содержать специальные символы — они будут корректно обработаны.

    Возвращает:
        List[Dict[str, Any]]: список транзакций (полных словарей),
            в поле 'description' которых найдено совпадение с search_string.
            Порядок транзакций соответствует порядку в исходном списке data.

    """
    if not search_string or not search_string.strip():
        return []

    result = []
    escaped_search = re.escape(search_string.lower())
    pattern = re.compile(escaped_search, re.IGNORECASE)

    for transaction in data:
        description = transaction.get('description', '')
        if description and pattern.search(description.lower()):
            result.append(transaction)

    return result
