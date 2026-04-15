import re
from collections import Counter
from typing import List, Dict, Any


def process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """
    Подсчитывает количество транзакций по заданным категориям на основе описания.

    Функция анализирует поле 'description' в каждой транзакции и проверяет, содержит ли оно
    точное совпадение с одной из указанных категорий (с учётом границ слов). Поиск выполняется
    с игнорированием регистра и корректным экранированием специальных символов в названиях категорий.

    Особенности работы:
    - регистронезависимый поиск (игнорирует различия в регистре букв);
    - поиск по границам слов (шаблон \b гарантирует, что 'супермаркет' не совпадет с 'супермаркеты');
    - автоматическое экранирование специальных символов в названиях категорий (точки, проценты и т. д.);
    - транзакции без поля 'description' или с пустым/пробеловым описанием пропускаются;
    - все указанные категории присутствуют в результате, даже если совпадений не найдено (счётчик = 0).

    Параметры:
        data (List[Dict[str, Any]]): список транзакций. Каждая транзакция — словарь,
            который может содержать поле 'description' с текстом описания операции.
            Другие поля игнорируются при анализе.
        categories (List[str]): список категорий для поиска. Каждая категория — строка,
            которая будет искаться как отдельное слово в описаниях транзакций.

    Возвращает:
        Dict[str, int]: словарь, где:
            - ключи — названия категорий из входного списка categories;
            - значения — количество транзакций, в описании которых найдено точное совпадение
              с соответствующей категорией (с учётом границ слов и игнорированием регистра).

    """
    category_counter = Counter({category: 0 for category in categories})

    for transaction in data:
        description = transaction.get('description', '')
        if not description or not description.strip():
            continue

        desc_lower = description.lower()

        for category in categories:
            escaped_category = re.escape(category.lower())
            pattern = re.compile(rf'\b{escaped_category}\b', re.IGNORECASE)

            if pattern.search(desc_lower):
                category_counter[category] += 1

    return dict(category_counter)
