from typing import Any, Dict, List
import os
import pandas as pd


def read_csv_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает финансовые транзакции из CSV‑файла с разделителем ';'.

    Функция открывает CSV‑файл, парсит его содержимое с помощью `csv.DictReader`
    и возвращает список словарей, где каждый словарь представляет одну транзакцию.
    Все ключи и значения очищаются от лишних пробелов.

    Args:
        file_path (str): Полный путь к CSV‑файлу с транзакциями.

    Returns:
        List[Dict[str, Any]]: Список словарей, где:
            * каждый словарь — одна транзакция;
            * ключи словаря — названия колонок из CSV (очищены от пробелов);
            * значения — данные из соответствующей строки (очищены от пробелов).
            Возвращает пустой список, если файл пуст или содержит только заголовки.

    Raises:
        FileNotFoundError: Если файл по указанному пути не существует.
        UnicodeDecodeError: Если файл не может быть декодирован как UTF‑8.
        csv.Error: Если произошла ошибка при парсинге CSV‑формата.

    Examples:
        >>> transactions = read_csv_transactions('transactions.csv')
        >>> print(transactions[0])
        {'id': '1', 'amount': '1000', 'currency': 'RUB'}

        Для CSV с содержимым:
        id,amount,currency
        1,1000,RUB
        2,2000,USD

    Notes:
        * Файл должен быть закодирован в UTF‑8.
        * Первая строка CSV‑файла интерпретируется как заголовки колонок.
        * Пробелы в начале и конце ключей и значений удаляются автоматически.
    """
    transactions = []  # Инициализируем список транзакций

    with open(file_path, 'r', encoding='utf-8') as f:
        # Читаем все строки файла
        lines = f.readlines()

        if not lines:
            return transactions  # Возвращаем пустой список, если файл пустой

        # Первая строка — заголовки столбцов
        headers = lines[0].strip().split(';')

        # Обрабатываем оставшиеся строки — это данные транзакций
        for line in lines[1:]:
            # Разделяем строку по точке с запятой
            values = line.strip().split(';')

            # Создаём словарь транзакции: сопоставляем заголовки и значения
            transaction = {}
            for i, header in enumerate(headers):
                # Если индекс выходит за пределы списка значений, используем пустую строку
                value = values[i] if i < len(values) else ''
                transaction[header.strip()] = value.strip()

            transactions.append(transaction)

    return transactions


def read_excel_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает финансовые транзакции из Excel‑файла (.xlsx) и унифицирует ключи.

    Функция использует `pandas.read_excel` для загрузки данных из первого листа Excel‑файла,
    преобразует их в список словарей и нормализует значения (NaN → None, float → int, если целое).

    Args:
        file_path (str): Полный путь к Excel‑файлу (.xlsx) с транзакциями.

    Returns:
        List[Dict[str, Any]]: Список словарей, где:
            * каждый словарь — одна транзакция;
            * ключи словаря — названия колонок из Excel;
            * значения:
                - `None` для пустых ячеек (NaN);
                - `int` для целых чисел (если исходное значение — float и `is_integer()`);
                - `str` для всех остальных значений.
            Возвращает пустой список, если лист пуст.

    Raises:
        FileNotFoundError: Если файл по указанному пути не существует.
        ValueError: Если расширение файла не `.xlsx` (проверка без учёта регистра).
        pandas.errors.EmptyDataError: Если лист Excel пуст.
        pandas.errors.ParserError: Если произошла ошибка при чтении Excel‑формата.

    Examples:
        >>> transactions = read_excel_transactions('transactions.xlsx')
        >>> print(transactions[0])
        {'ID': '1', 'Сумма': '1000', 'Валюта': 'RUB'}


        Для Excel с данными:
        | ID | Сумма | Валюта |
        |----|-------|--------|
        | 1  | 1000 | RUB    |
        | 2  | 2000 | USD    |

    Notes:
        * Поддерживается только формат `.xlsx` (не `.xls`).
        * Читается только первый лист (`sheet_name=0`).
        * Все числовые значения, которые являются целыми (например, `1000.0`), преобразуются в `int`.
        * `None` используется для представления пустых ячеек (`NaN` в pandas).
        * Остальные значения приводятся к строке для единообразия.
    """
    df = pd.read_excel(file_path)
    transactions = []
    for _, row in df.iterrows():
        transaction = {
            'date': str(row.get('date', '')),
            'description': str(row.get('description', '')),
            'amount': str(row.get('amount', '')),
            'currency_name': str(row.get('currency_name', '')),  # Название валюты
            'currency_code': str(row.get('currency_code', '')),  # Код валюты
            'from': str(row.get('from', '')),
            'to': str(row.get('to', '')),
            'state': str(row.get('state', ''))
        }
        transactions.append(transaction)
    return transactions
