import pytest
from typing import List, Dict, Any, Callable, Generator
from ..src.generators import filter_by_currency, transaction_descriptions, card_number_generator


# --- ФИКСТУРА С ТЕСТОВЫМИ ДАННЫМИ filter_by_currency b transaction_descriptions ---
@pytest.fixture
def transactions() -> List[Dict[str, Any]]:
    """Фикстура с тестовыми транзакциями."""
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {
                "amount": "9824.07",
                "currency": {
                    "name": "USD",
                    "code": "USD"
                }
            },
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702"
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {
                "amount": "79114.93",
                "currency": {
                    "name": "USD",
                    "code": "USD"
                }
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188"
        },
        {
            "id": 873106923,
            "state": "EXECUTED",
            "date": "2019-03-23T01:09:46.296404",
            "operationAmount": {
                "amount": "43318.34",
                "currency": {
                    "name": "руб.",
                    "code": "RUB"
                }
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 44812258784861134719",
            "to": "Счет 74489636417521191160"
        },
        {
            "id": 895315941,
            "state": "EXECUTED",
            "date": "2018-08-19T04:27:37.904916",
            "operationAmount": {
                "amount": "56883.54",
                "currency": {
                    "name": "USD",
                    "code": "USD"
                }
            },
            "description": "Перевод с карты на карту",
            "from": "Visa Classic 6831982476737658",
            "to": "Visa Platinum 8990922113665229"
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount": {
                "amount": "67314.70",
                "currency": {
                    "name": "руб.",
                    "code": "RUB"
                }
            },
            "description": "Перевод организации",
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14211924144426031657"
        }
    ]


@pytest.fixture
def edge_cases() -> List[tuple]:
    """Фикстура с граничными случаями."""
    max_value = 9_999_999_999_999_999
    return [
        (1, 1, ["0001 0000 0000 0001"]),  # минимальная граница
        (max_value, max_value, ["9999 9999 9999 9999"])  # максимальная граница
    ]


# --- ТЕСТЫ ДЛЯ filter_by_currency ---


def test_filter_by_currency_usd_code(transactions: List[Dict[str, Any]]) -> None:
    """Тест фильтрации транзакций по коду валюты USD."""
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 3
    for transaction in result:
        assert transaction["operationAmount"]["currency"]["code"] == "USD"


def test_filter_by_currency_rub_code(transactions: List[Dict[str, Any]]) -> None:
    """Тест фильтрации транзакций по коду валюты RUB."""
    result = list(filter_by_currency(transactions, "RUB"))
    assert len(result) == 1
    for transaction in result:
        assert transaction["operationAmount"]["currency"]["code"] == "RUB"


def test_filter_by_currency_nonexistent_currency(transactions: List[Dict[str, Any]]) -> None:
    """Тест фильтрации по несуществующей валюте — должен вернуть пустой список."""
    result = list(filter_by_currency(transactions, "EUR"))
    assert result == []


def test_filter_by_currency_empty_list() -> None:
    """Тест с пустым списком транзакций."""
    empty_transactions: List[Dict[str, Any]] = []
    result = list(filter_by_currency(empty_transactions, "USD"))
    assert result == []


# --- ТЕСТЫ ДЛЯ transaction_descriptions ---


def test_transaction_descriptions_all_transactions(transactions: List[Dict[str, Any]]) -> None:
    """Тест получения описаний для всех транзакций."""
    expected = [
        "Перевод организации",
        "Перевод со счета на счет",
        "Перевод со счета на счет",
        "Перевод с карты на карту"
    ]
    result = list(transaction_descriptions(transactions))
    assert result == expected


def test_transaction_descriptions_single_transaction(transactions: List[Dict[str, Any]]) -> None:
    """Тест для одной транзакции."""
    single_transaction = [transactions[0]]
    expected = ["Перевод организации"]
    result = list(transaction_descriptions(single_transaction))
    assert result == expected


def test_transaction_descriptions_empty_list() -> None:
    """Тест с пустым списком транзакций для transaction_descriptions."""
    empty_transactions: List[Dict[str, Any]] = []
    result = list(transaction_descriptions(empty_transactions))
    assert result == []


# --- ТЕСТЫ ДЛЯ card_number_generator ---

@pytest.fixture
def card_generator() -> Callable[[int, int], Generator[str, None, None]]:
    def _generator(start: int, end: int) -> Generator[str, None, None]:
        return card_number_generator(start, end)

    return _generator


# Тест 1: Базовые случаи — проверка корректного форматирования
@pytest.mark.parametrize("number,expected", [
    (1, "0000 0000 0000 0001"),
    (42, "0000 0000 0000 0042"),
    (123, "0000 0000 0000 0123"),
    (1234, "0000 0000 0000 1234"),
    (12345, "0000 0000 0001 2345"),
    (12345678, "0000 0000 1234 5678"),
    (123456789012, "0000 1234 5678 9012"),
    (9999999999999999, "9999 9999 9999 9999"),
])
def test_card_formatting(
        card_generator: Callable[[int, int], Generator[str, None, None]],
        number: int,
        expected: str
) -> None:
    """Тест: генератор правильно форматирует отдельные номера карт."""
    generator = card_generator(number, number)
    result = next(generator)
    assert result == expected


# Тест 2: Проверка диапазона номеров
@pytest.mark.parametrize("start,end,expected_list", [
    (1, 3, [
        "0000 0000 0000 0001",
        "0000 0000 0000 0002",
        "0000 0000 0000 0003"
    ]),
    (100, 102, [
        "0000 0000 0000 0100",
        "0000 0000 0000 0101",
        "0000 0000 0000 0102"
    ]),
])
def test_range_generation(
        card_generator: Callable[[int, int], Generator[str, None, None]],
        start: int,
        end: int,
        expected_list: List[str]
) -> None:
    """Тест: генератор корректно генерирует номера в заданном диапазоне."""
    generator = card_generator(start, end)
    results = list(generator)
    assert results == expected_list


# Тест 3: Проверка граничных значений

def test_edge_values(card_generator: Callable[[int, int], Generator[str, None, None]]) -> None:
    """Тест: генератор корректно обрабатывает крайние значения диапазона."""
    # Минимальная граница
    min_generator = card_generator(1, 1)
    min_result = next(min_generator)
    assert min_result == "0000 0000 0000 0001"

    # Максимальная граница
    max_generator = card_generator(9999999999999999, 9999999999999999)
    max_result = next(max_generator)
    assert max_result == "9999 9999 9999 9999"


# Тест 4: Проверка ленивой генерации (генератор не вычисляет все значения сразу)
def test_lazy_generation(card_generator):
    """Тест: генератор работает лениво и не вычисляет все значения заранее."""
    generator = card_generator(1, 1000)

    # Берём только первые 5 элементов
    first_five = [next(generator) for _ in range(5)]

    expected = [
        "0000 0000 0000 0001",
        "0000 0000 0000 0002",
        "0000 0000 0000 0003",
        "0000 0000 0000 0004",
        "0000 0000 0000 0005"
    ]
    assert first_five == expected


# Тест 5: Проверка обработки ошибок для некорректных диапазонов
@pytest.mark.parametrize("start,end,error_message", [
    (5, 3, "Начальное значение не может быть больше конечного"),
    (0, 5, "Начальное значение должно быть не менее 1"),
    (1, 10_000_000_000_000_000, "Конечное значение не может превышать 9999999999999999")
])
def test_invalid_ranges(card_generator, start, end, error_message):
    """Тест: обработка ошибок для некорректных входных данных."""
    with pytest.raises(ValueError, match=error_message):
        generator = card_generator(start, end)
        list(generator)


# Тест 6: Проверка большого диапазона
def test_large_range(card_generator):
    """Тест: генератор корректно работает с большими диапазонами."""
    generator = card_generator(9999999999999997, 9999999999999999)
    results = list(generator)

    expected = [
        "9999 9999 9999 9997",
        "9999 9999 9999 9998",
        "9999 9999 9999 9999"
    ]
    assert results == expected


# Тест 7: Проверка одиночного элемента
def test_single_element(card_generator):
    """Тест: генератор корректно обрабатывает диапазон из одного элемента."""
    generator = card_generator(42, 42)
    results = list(generator)
    assert results == ["0000 0000 0000 0042"]


# Тест 8: Проверка производительности на большом количестве элементов
def test_performance_large_count(card_generator):
    """Тест: генератор может обработать большое количество элементов без ошибок."""
    generator = card_generator(1, 1000)
    count = sum(1 for _ in generator)  # Считаем количество элементов
    assert count == 1000


# Тест 9: Проверка корректности длины номера карты
@pytest.mark.parametrize("number", [1, 42, 123456789012, 9999999999999999])
def test_card_length(card_generator, number):
    """Тест: все номера карт имеют правильную длину (19 символов с пробелами)."""
    generator = card_generator(number, number)
    card = next(generator)
    # 16 цифр + 3 пробела = 19 символов
    assert len(card) == 19
    # Проверяем, что формат соответствует XXXX XXXX XXXX XXXX
    assert card[4] == ' ' and card[9] == ' ' and card[14] == ' '


# Тест 10: Проверка на отсутствие лишних пробелов или символов

def test_no_extra_characters(card_generator):
    """Тест: номера карт не содержат лишних символов или пробелов."""
    generator = card_generator(1234, 1234)
    card = next(generator)
    # Разбиваем на блоки и проверяем, что каждый блок — 4 цифры
    blocks = card.split()
    assert len(blocks) == 4
    for block in blocks:
        assert len(block) == 4
        assert block.isdigit()  # Каждый блок состоит только из цифр
