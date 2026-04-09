import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from count_module import process_bank_operations
from file_reader import read_csv_transactions, read_excel_transactions
from search_module import process_bank_search


def load_json_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из JSON‑файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_transaction(transaction: Dict[str, Any]) -> str:
    """Форматирует транзакцию для вывода в консоль."""
    date = transaction.get('date', 'N/A')
    description = transaction.get('description', 'N/A')
    amount = transaction.get('amount', 'N/A')
    currency = transaction.get('currency', 'N/A')

    formatted = f"{date} {description}\n"

    from_account = transaction.get('from', '')
    to_account = transaction.get('to', '')

    if from_account and to_account:
        formatted += f"{from_account} -> {to_account}\n"
    elif from_account:
        formatted += f"{from_account}\n"
    elif to_account:
        formatted += f"{to_account}\n"

    formatted += f"Сумма: {amount} {currency}"
    return formatted


def parse_date(date_str: str) -> datetime:
    """Преобразует строку даты в объект datetime."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        # Если формат не подходит, возвращаем минимальную дату
        return datetime.min


def main():
    # Папка с данными относительно расположения main.py
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"  # папка data на уровень выше src/

    DEFAULT_FILES = {
        'json': data_dir / "transactions.json",
        'csv': data_dir / "transactions.csv",
        'xlsx': data_dir / "transactions_excel.xlsx"
    }

    print("Программа: Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    # Словарь для нормализации ввода статусов
    STATUS_CANONICAL = {
        'executed': 'EXECUTED',
        'cancelled': 'CANCELED',
        'canceled': 'CANCELED',  # Поддержка американского варианта написания
        'pending': 'PENDING'
    }
    AVAILABLE_STATUSES = list(STATUS_CANONICAL.values())
    DEFAULT_CATEGORIES = ['супермаркет', 'ресторан', 'транспорт', 'аптека', 'перевод']

    transactions = None  # Инициализируем переменную для хранения транзакций

    while True:
        print("\nВыберите необходимый пункт меню:")
        print("1. Получить информацию о транзакциях из JSON‑файла")
        print("2. Получить информацию о транзакциях из CSV‑файла")
        print("3. Получить информацию о транзакциях из XLSX‑файла")
        print("4. Подсчитать транзакции по категориям")
        print("0. Выход")

        choice = input("\nПользователь: ").strip()

        if choice == '0':
            print("Программа: До свидания!")
            break

        elif choice in ['1', '2', '3']:
            file_path = input("Программа: Введите путь к файлу: ").strip()
            file_exists = Path(file_path).exists()

            if not file_exists:
                print(f"Программа: Ошибка: файл '{file_path}' не найден.")
                continue

            try:
                if choice == '1':
                    print("Программа: Для обработки выбран JSON‑файл.")
                    transactions = load_json_transactions(file_path)
                elif choice == '2':
                    print("Программа: Для обработки выбран CSV‑файл.")
                    transactions = read_csv_transactions(file_path)
                elif choice == '3':
                    print("Программа: Для обработки выбран XLSX‑файл.")
                    transactions = read_excel_transactions(file_path)

                # Проверка на пустой файл
                if not transactions:
                    print("Программа: Предупреждение: файл загружен, но не содержит транзакций.")
                    continue

                print(f"Программа: Успешно загружено {len(transactions)} транзакций.")

                # Начинаем цикл фильтрации по статусу
                while True:
                    print("\nПрограмма: Введите статус, по которому необходимо выполнить фильтрацию.")
                    print(f"Доступные для фильтровки статусы: {', '.join(AVAILABLE_STATUSES)}")
                    status_filter_input = input("Пользователь: ").strip().lower()

                    # Проверка на пустой ввод
                    if not status_filter_input:
                        print("Программа: Статус не может быть пустым. Попробуйте снова.")
                        continue

                    if status_filter_input in STATUS_CANONICAL:
                        status_filter = STATUS_CANONICAL[status_filter_input]
                        print(f"Программа: Операции отфильтрованы по статусу \"{status_filter}\"")
                        filtered_transactions = [
                            t for t in transactions
                            if t.get('status', '').strip().upper() == status_filter
                        ]
                        print(f"Программа: После фильтрации по статусу осталось {len(filtered_transactions)} транзакций")
                        break  # Выход из цикла
                    else:
                        print(f"Программа: Статус операции \"{status_filter_input}\" недоступен.")
                # Цикл продолжается — снова запрашиваем ввод

                # 2. СОРТИРОВКА ПО ДАТЕ (после цикла фильтрации по статусу)
                sort_by_date = input(
                    "Программа: Отсортировать операции по дате? Да/Нет\nПользователь: "
                ).strip().lower()

                if sort_by_date in ['да', 'yes', 'y']:
                    sort_order = input(
                        "Программа: Отсортировать по возрастанию или по убыванию?\nПользователь: "
                    ).strip().lower()
                    reverse_order = False
                    if 'убыванию' in sort_order:
                        reverse_order = True
                    elif 'возрастанию' not in sort_order:
                        print("Программа: Нераспознанный порядок сортировки. Используется сортировка по возрастанию.")

                    # Проверка наличия поля 'date' у транзакций
                    transactions_with_date = [
                        t for t in filtered_transactions
                        if 'date' in t and t['date']
                    ]

                    if transactions_with_date:
                        filtered_transactions.sort(
                            key=lambda x: parse_date(x.get('date', '')),
                            reverse=reverse_order
                        )
                        print("Программа: Сортировка по дате выполнена успешно.")
                    else:
                        print(
                            "Программа: Предупреждение: поле 'date' отсутствует во всех транзакциях. Сортировка не выполнена.")

                # 3. ФИЛЬТРАЦИЯ ПО ВАЛЮТЕ (после сортировки)
                only_rub = input(
                    "Программа: Выводить только рублёвые транзакции? Да/Нет\nПользователь: "
                ).strip().lower()
                if only_rub in ['да', 'yes', 'y']:
                    filtered_transactions = [
                        t for t in filtered_transactions
                        if t.get('currency', '').strip().upper() == 'RUB'
                    ]
                    print(f"Программа: После фильтрации по валюте осталось {len(filtered_transactions)} транзакций.")

                # 4. ПОИСК ПО ОПИСАНИЮ (после фильтрации по валюте)
                search_by_desc = input(
                    "Программа: Отфильтровать список транзакций по определённому слову в описании? Да/Нет\nПользователь: "
                ).strip().lower()

                if search_by_desc in ['да', 'yes', 'y']:
                    search_term = input("Программа: Введите слово для поиска в описании: ").strip()
                    if search_term:
                        filtered_transactions = process_bank_search(filtered_transactions, search_term)
                        print(f"Программа: После поиска по описанию осталось {len(filtered_transactions)} транзакций.")
                    else:
                        print("Программа: Пустое слово для поиска. Поиск не выполнен.")

                # 5. ВЫВОД РЕЗУЛЬТАТОВ (финальный этап)
                print("\nПрограмма: Распечатываю итоговый список транзакций...")
                if not filtered_transactions:
                    print("Программа: Не найдено ни одной транзакции, подходящей под ваши условия фильтрации.")
                else:
                    print(f"\nПрограмма: Всего банковских операций в выборке: {len(filtered_transactions)}")
                    try:
                        for i, transaction in enumerate(filtered_transactions, 1):
                            print(f"\n{i}. {format_transaction(transaction)}")
                    except Exception as e:
                        print(f"Программа: Ошибка при форматировании транзакции: {e}")

            except Exception as e:
                print(f"Программа: Ошибка при загрузке файла: {e}")
                continue

        elif choice == '4':
            # Логика для подсчёта транзакций по категориям
            if transactions is None or not transactions:
                print("Программа: Сначала загрузите данные о транзакциях!")
                continue

    try:
        print("\nПрограмма: Подсчёт транзакций по категориям...")
        print(f"Используемые категории: {', '.join(DEFAULT_CATEGORIES)}")
        category_results = process_bank_operations(transactions, DEFAULT_CATEGORIES)
        print("\nПрограмма: Статистика по категориям:")
        for category, count in category_results.items():
            print(f"{category}: {count} операций")
    except Exception as e:
        print(f"Программа: Ошибка при подсчёте транзакций по категориям: {e}")

    # Завершение основного цикла while True

    if __name__ == "__main__":
        main()
