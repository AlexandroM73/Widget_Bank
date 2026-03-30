import csv
import os
import pandas as pd
from typing import List, Dict, Any


def read_csv_transactions(file_path: str) -> List[Dict[str, Any]]:
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

# import csv
# import os
# import pandas as pd
# from typing import List, Dict, Any
#
# def read_csv_transactions(file_path: str) -> List[Dict[str, Any]]:
#     """
#     Читает финансовые транзакции из CSV‑файла.
#     Args:
#         file_path (str): путь к CSV‑файлу.
#     Returns:
#         List[Dict[str, Any]]: список словарей с данными о транзакциях;
#             пустой список, если файл не найден или пуст.
#     Raises:
#         FileNotFoundError: если файл не существует.
#         Exception: если произошла ошибка при чтении файла.
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Файл не найден: {file_path}")
#
#     transactions = []
#
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             # Используем DictReader для автоматического преобразования в словари
#             csv_reader = csv.DictReader(file)
#
#             for row in csv_reader:
#                 # Очищаем данные от лишних пробелов
#                 cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
#                 transactions.append(cleaned_row)
#         return transactions
#
#     except Exception as e:
#         raise Exception(f"Ошибка при чтении CSV‑файла {file_path}: {e}")
#
#
# def read_excel_transactions(file_path: str) -> List[Dict[str, Any]]:
#     """
#     Читает финансовые транзакции из Excel‑файла (.xlsx).
#     Args:
#         file_path (str): путь к Excel‑файлу (.xlsx).
#     Returns:
#         List[Dict[str, Any]]: список словарей с данными о транзакциях;
#             пустой список, если файл не найден или пуст.
#     Raises:
#         FileNotFoundError: если файл не существует.
#         ValueError: если расширение файла не .xlsx.
#         Exception: если произошла ошибка при чтении файла.
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Файл не найден: {file_path}")
#
#     if not file_path.lower().endswith('.xlsx'):
#         raise ValueError(f"Ожидался файл .xlsx, получен: {file_path}")
#
#
#     try:
#         # Читаем все листы, берём первый
#         df = pd.read_excel(file_path, sheet_name=0)
#         # Конвертируем DataFrame в список словарей
#         transactions = df.to_dict('records')
#         # Преобразуем значения в строки для единообразия
#         for transaction in transactions:
#             for key, value in transaction.items():
#                 if pd.isna(value):
#                     transaction[key] = None
#                 else:
#                     transaction[key] = str(value) if not isinstance(value, (int, float)) else value
#         return transactions
#
#     except Exception as e:
#         raise Exception(f"Ошибка при чтении Excel‑файла {file_path}: {e}")
