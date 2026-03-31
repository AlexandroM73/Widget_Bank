import csv
import os
from typing import Any, Dict, List

import pandas as pd


def read_csv_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает финансовые транзакции из CSV‑файла.

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
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    transactions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
            transactions.append(cleaned_row)
    return transactions


def read_excel_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает финансовые транзакции из Excel‑файла (.xlsx).

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
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    if not file_path.lower().endswith('.xlsx'):
        raise ValueError(f"Ожидался файл .xlsx, получен: {file_path}")

    df = pd.read_excel(file_path, sheet_name=0)
    transactions = df.to_dict('records')

    for transaction in transactions:
        for key, value in transaction.items():
            if pd.isna(value):
                transaction[key] = None
            else:
                # Если значение — число с плавающей точкой и оно целое, преобразуем в int
                if isinstance(value, float) and value.is_integer():
                    value = int(value)
                # Конвертируем в строку
                transaction[key] = str(value)

    return transactions
