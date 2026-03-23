from typing import Generator


def filter_by_currency(transactions, currency_code):
    """Фильтрует транзакции по коду или названию валюты."""
    for transaction in transactions:
        # Проверяем, что транзакция выполнена
        if transaction.get("state") != "EXECUTED":
            continue

        # Получаем данные о валюте
        operation_amount = transaction.get("operationAmount", {})
        currency_data = operation_amount.get("currency", {})

        # Сравниваем с кодом и названием валюты
        if (currency_data.get("code") == currency_code or
                currency_data.get("name") == currency_code):
            yield transaction


def transaction_descriptions(transactions):
    """Возвращает описания транзакций для выполненных операций."""
    for transaction in transactions:
        if transaction.get("state") == "EXECUTED":
            description = transaction.get("description")
            if description:  # проверяем, что поле существует
                yield description


def card_number_generator(start: int, end: int) -> Generator[str, None, None]:
    """
        Генератор номеров банковских карт в формате 'XXXX XXXX XXXX XXXX'.

        Принимает начальное и конечное значения для генерации диапазона номеров.
        Диапазон допустимых значений: от 1 до 9 999 999 999 999 999.

        Args:
            start (int): Начальное число диапазона (включительно).
            end (int): Конечное число диапазона (включительно).

        Yields:
            str: Номер карты в формате 'XXXX XXXX XXXX XXXX'.

        Raises:
            ValueError: Если start > end или значения выходят за допустимый диапазон.
        """

    MAX_VALUE = 9_999_999_999_999_999

    if start > end:
        raise ValueError("Начальное значение не может быть больше конечного")
    if start < 1:
        raise ValueError("Начальное значение должно быть не менее 1")
    if end > MAX_VALUE:
        raise ValueError(f"Конечное значение не может превышать {MAX_VALUE}")

    for number in range(start, end + 1):
        num_str = str(number)
        result = ['0'] * 16

        # Заполняем справа налево, начиная с последней позиции (15)
        num_idx = 0
        for pos in range(15, -1, -1):  # Идём от 15 до 0
            if num_idx < len(num_str):
                result[pos] = num_str[-(num_idx + 1)]  # Берём цифру с конца числа
                num_idx += 1
            else:
                break

        num_str_full = ''.join(result)
        blocks = [num_str_full[i:i+4] for i in range(0, 16, 4)]
        formatted = ' '.join(blocks)
        yield formatted
