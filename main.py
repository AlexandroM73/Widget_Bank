import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from widget import mask_account_card
from count_module import process_bank_operations
from file_reader import read_csv_transactions, read_excel_transactions
from search_module import process_bank_search


def setup_src_path():
    """Добавляет папку src в sys.path, если она существует."""
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))


# Вызываем функцию настройки пути ПОСЛЕ всех импортов
setup_src_path()


def load_json_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из JSON‑файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_transaction(transaction: Dict[str, Any]) -> str:
    # Обработка даты
    date_raw = transaction.get('date')
    if date_raw:
        date = parse_iso_date(date_raw)
    else:
        date = 'Дата отсутствует'

    description = transaction.get('description', 'Описание отсутствует')

    # Обработка суммы из вложенной структуры operationAmount
    operation_amount = transaction.get('operationAmount')
    if operation_amount and isinstance(operation_amount, dict):
        amount_value = operation_amount.get('amount')
        currency_info = operation_amount.get('currency')

        if amount_value is not None and str(amount_value).strip():
            amount = str(amount_value).strip()
        else:
            amount = 'Сумма не указана'

        # Обработка валюты из вложенной структуры
        if currency_info and isinstance(currency_info, dict):
            currency_name_value = currency_info.get('name')
            currency_code_value = currency_info.get('code')

            if currency_name_value is not None and str(currency_name_value).strip():
                currency_name = str(currency_name_value).strip()
            else:
                currency_name = 'Название валюты отсутствует'

            if currency_code_value is not None and str(currency_code_value).strip():
                currency_code = str(currency_code_value).strip()
            else:
                currency_code = 'Код валюты отсутствует'
        else:
            currency_name = 'Название валюты отсутствует'
            currency_code = 'Код валюты отсутствует'
    else:
        # Резервный поиск плоских полей (для совместимости с другими форматами)
        amount = (
                transaction.get('amount') or
                transaction.get('Amount') or
                transaction.get('AMOUNT') or
                transaction.get('sum') or
                transaction.get('Sum') or
                transaction.get('SUM') or
                'Сумма не указана'
        )

        currency_name = (
                transaction.get('name') or
                transaction.get('Name') or
                transaction.get('NAME') or
                transaction.get('currency_name') or
                transaction.get('Currency_Name') or
                transaction.get('CURRENCY_NAME') or
                'Название валюты отсутствует'
        )

        currency_code = (
                transaction.get('code') or
                transaction.get('Code') or
                transaction.get('CODE') or
                transaction.get('currency_code') or
                transaction.get('Currency_Code') or
                transaction.get('CURRENCY_CODE') or
                'Код валюты отсутствует'
        )

    formatted = f"{date} {description}\n"

    from_account = transaction.get('from', '')
    to_account = transaction.get('to', '')

    # Маскировка счетов/карт
    if from_account:
        try:
            from_account_masked = mask_account_card(from_account)
        except ValueError:
            from_account_masked = f"Счёт/карта (некорректные данные: {from_account})"
    else:
        from_account_masked = ''

    if to_account:
        try:
            to_account_masked = mask_account_card(to_account)
        except ValueError:
            to_account_masked = f"Счёт/карта (некорректные данные: {to_account})"
    else:
        to_account_masked = ''

    # Форматирование строки перевода
    if from_account_masked and to_account_masked:
        formatted += f"{from_account_masked} -> {to_account_masked}\n"
    elif from_account_masked:
        formatted += f"{from_account_masked}\n"
    elif to_account_masked:
        formatted += f"{to_account_masked}\n"

    # Вывод суммы с названием и кодом валюты
    formatted += f"Сумма: {amount} {currency_name} ({currency_code})"
    return formatted


def parse_iso_date(date_str: str) -> str:
    """
    Парсит дату в формате ISO 8601 (включая Z в конце) и возвращает в формате ДД.ММ.ГГГГ.
    Если дата некорректна, возвращает 'Дата некорректна'.
    """
    if not date_str:
        return 'Дата отсутствует'

    # Удаляем 'Z' в конце, если есть (обозначает UTC)
    if date_str.endswith('Z'):
        date_str = date_str[:-1]

    # Пробуем разные форматы ISO 8601
    formats = [
        '%Y-%m-%dT%H:%M:%S.%f',  # С микросекундами
        '%Y-%m-%dT%H:%M:%S',  # Без микросекунд
        '%Y-%m-%d %H:%M:%S',  # Пробел вместо T
        '%Y-%m-%d'  # Только дата
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%d.%m.%Y')
        except ValueError:
            continue

    return 'Дата некорректна'


def safe_parse_date(date_str: str) -> datetime:
    """
    Безопасный парсинг даты для сортировки. Поддерживает разные форматы.
    Возвращает datetime.min, если дата не распознана.
    """
    if not date_str:
        return datetime.min

    # Нормализуем строку: удаляем лишние пробелы и Z (UTC)
    date_str = date_str.strip()
    if date_str.endswith('Z'):
        date_str = date_str[:-1]

    # Список форматов для попытки парсинга
    formats = [
        '%Y-%m-%dT%H:%M:%S.%f',  # ISO с микросекундами
        '%Y-%m-%dT%H:%M:%S',  # ISO без микросекунд
        '%Y-%m-%d %H:%M:%S',  # ISO с пробелом вместо T
        '%Y-%m-%d',  # Только дата ISO
        '%d.%m.%Y %H:%M:%S',  # Русский с временем
        '%d.%m.%Y',  # Русский формат
        '%m/%d/%Y %H:%M:%S',  # Американский с временем
        '%m/%d/%Y',  # Американский формат
        '%Y/%m/%d',  # Год/месяц/день
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return datetime.min  # Если ни один формат не подошёл


def get_currency_code(transaction: Dict[str, Any]) -> str:
    """Извлекает код валюты из транзакции."""
    # JSON: operationAmount.currency.code
    if 'operationAmount' in transaction:
        operation_amount = transaction['operationAmount']
        if isinstance(operation_amount, dict) and 'currency' in operation_amount:
            currency = operation_amount['currency']
            if isinstance(currency, dict) and 'code' in currency:
                return str(currency['code']).strip().upper()

    # CSV/XLSX и другие варианты: ищем разные названия поля
    currency_fields = ['currency_code', 'currency', 'currencyCode', 'curr_code']
    for field in currency_fields:
        if field in transaction:
            return str(transaction[field]).strip().upper()

    # Нормализация обозначений рубля
    code = str(transaction.get('currency_code', '')).strip().upper()
    if code in ['РУБ', 'РУБ.', 'RUBLE']:
        return 'RUB'

    return ''


def main():
    # Папка с данными относительно расположения main.py
    transactions = []  # Инициализируем переменную для хранения транзакций
    filtered_transactions = []  # Инициализируем пустой список
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"  # папка data

    # Проверяем существование папки data
    if not data_dir.exists():
        print(f"Программа: Предупреждение: папка '{data_dir}' не найдена. Создаю...")
        data_dir.mkdir(exist_ok=True)

    DEFAULT_FILES = {
        'json': data_dir / "transactions.json",
        'csv': data_dir / "transactions.csv",
        'xlsx': data_dir / "transactions_excel.xlsx"
    }

    print("Программа: Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    # Словарь для нормализации ввода статусов
    AVAILABLE_STATUSES = ['EXECUTED', 'CANCELED', 'PENDING']
    DEFAULT_CATEGORIES = ['супермаркет', 'ресторан', 'транспорт', 'аптека', 'перевод']

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
            # Определяем тип файла и соответствующий дефолтный путь
            file_type = {
                '1': 'json',
                '2': 'csv',
                '3': 'xlsx'
            }[choice]
            default_file = DEFAULT_FILES[file_type]

            # Запрашиваем путь у пользователя
            user_input = input(
                f"Программа: Введите путь к файлу (или нажмите Enter "
                f"для использования стандартного пути: {default_file}): "
            ).strip()

            # Если ввод пустой, используем дефолтный путь
            if not user_input:
                file_path = default_file
                print(f"Программа: Используется стандартный путь: {file_path}")
            else:
                file_path = Path(user_input)
                print(f"Программа: Используется указанный путь: {file_path}")

            file_exists = file_path.exists()
            if not file_exists:
                print(f"Программа: Ошибка: файл '{file_path}' не найден.")
                continue

            try:
                # Преобразуем Path в строку для операций со строками
                file_path_str = str(file_path)

                if choice == '1':
                    print("Программа: Для обработки выбран JSON‑файл.")
                    transactions = load_json_transactions(file_path_str)
                elif choice == '2':
                    print("Программа: Для обработки выбран CSV‑файл.")
                    transactions = read_csv_transactions(file_path_str)
                elif choice == '3':
                    print("Программа: Для обработки выбран XLSX‑файл.")
                    # Проверяем расширение файла (преобразуем в строку)
                    if not file_path_str.lower().endswith('.xlsx'):
                        raise ValueError(f"Ожидался файл .xlsx, получен: {file_path_str}")
                    transactions = read_excel_transactions(file_path_str)

                # Проверка на пустой файл
                if not transactions:
                    print("Программа: Предупреждение: файл загружен, но не содержит транзакций.")
                    continue

                print(f"Программа: Успешно загружено {len(transactions)} транзакций.")

                # Начинаем цикл фильтрации по статусу
                while True:
                    print("\nПрограмма: Введите статус, по которому необходимо выполнить фильтрацию.")
                    print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")
                    # print(f"Доступные для фильтровки статусы: {', '.join(AVAILABLE_STATUSES)}")
                    status_filter_input = input("Пользователь: ").strip().lower()

                    # Проверка на пустой ввод
                    if not status_filter_input:
                        print("Программа: Статус не может быть пустым. Попробуйте снова.")
                        continue

                    # Приводим ввод к верхнему регистру для сравнения
                    status_filter_upper = status_filter_input.upper()

                    # Проверяем, что статус есть в списке доступных
                    if status_filter_upper in AVAILABLE_STATUSES:
                        print(f"Программа: Операции отфильтрованы по статусу \"{status_filter_upper}\"")
                        filtered_transactions = []
                        for t in transactions:
                            state = t.get('state')
                            if state is None:
                                continue  # Пропускаем транзакции без статуса
                            if str(state).strip().upper() == status_filter_upper:
                                filtered_transactions.append(t)

                        print(
                            f"Программа: После фильтрации по статусу осталось {len(filtered_transactions)} транзакций")
                        break  # Выход из цикла
                    else:
                        count = len(filtered_transactions)
                        print(f"Программа: После фильтрации по статусу осталось {count} транзакций")

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

                    # Фильтруем транзакции, у которых есть поле 'date'
                    transactions_with_date = [
                        t for t in filtered_transactions
                        if t.get('date')
                    ]

                    if transactions_with_date:
                        # Сортируем по дате с использованием улучшенной функции парсинга
                        filtered_transactions.sort(
                            key=lambda x: safe_parse_date(x.get('date', '')),
                            reverse=reverse_order
                        )
                        print("Программа: Сортировка по дате выполнена успешно.")
                    else:
                        prefix = "Программа: После поиска по описанию"
                        count = len(filtered_transactions)
                        print(f"{prefix} осталось {count} транзакций.")

                # 3. ФИЛЬТРАЦИЯ ПО ВАЛЮТЕ (после сортировки)
                only_rub = input(
                    "Программа: Выводить только рублёвые транзакции? Да/Нет\nПользователь: "
                ).strip().lower()
                if only_rub in ['да', 'yes', 'y']:
                    filtered_transactions = [
                        t for t in filtered_transactions
                        if get_currency_code(t) == 'RUB'
                    ]
                    print(f"Программа: После фильтрации по валюте осталось {len(filtered_transactions)} транзакций.")

                # # 3. ФИЛЬТРАЦИЯ ПО ВАЛЮТЕ (после сортировки)
                # only_rub = input(
                #     "Программа: Выводить только рублёвые транзакции? Да/Нет\nПользователь: "
                # ).strip().lower()
                # if only_rub in ['да', 'yes', 'y']:
                #     filtered_transactions = [
                #         t for t in filtered_transactions
                #         if t.get('currency_code', '').strip().upper() == 'RUB'
                #     ]
                #     print(f"Программа: После фильтрации по валюте осталось {len(filtered_transactions)} транзакций.")

                # 4. ПОИСК ПО ОПИСАНИЮ (после фильтрации по валюте)
                search_by_desc = input(
                    "Программа: Отфильтровать список транзакций по слову в описании? Да/Нет\nПользователь: "
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
