import pytest
from typing import List, Dict, Any
from unittest.mock import mock_open, patch


@pytest.fixture
def mock_csv_file(request):
    """Фикстура, создающая мок для open с заданными CSV‑данными."""
    data = request.param if hasattr(request, 'param') else ""
    mock = mock_open(read_data=data)
    with patch('builtins.open', mock) as mock_patch:
        yield mock_patch


@pytest.fixture
def mock_file_exists():
    with patch('file_reader.os.path.exists') as mock:
        yield mock


@pytest.fixture
def mock_builtins_open():
    # Создаём мок с данными по умолчанию (можно переопределить в тестах)
    mock = mock_open(read_data="")
    with patch('builtins.open', mock) as mock_patch:
        yield mock_patch


@pytest.fixture
def csv_sample_data():
    return "id,amount,currency\n1,1000,RUB\n2,2000,USD"


@pytest.fixture
def empty_csv_data():
    return ""


@pytest.fixture
def headers_only_csv_data():
    return "id,amount,currency"


@pytest.fixture
def csv_with_spaces_data():
    return " id , amount , currency \n 1 , 1000 , RUB "


@pytest.fixture
def valid_card_numbers():
    """Фикстура с валидными номерами карт (16 цифр)."""
    return [
        1234567890123456,
        "1234567890123456",
        4532123456789012,
        "4532123456789012",
        9999888877776666,
        "9999888877776666"
    ]


@pytest.fixture
def invalid_card_lengths():
    """Фикстура с номерами карт некорректной длины."""
    return [
        {"input": 1234, "expected_error": "Номер карты должен содержать 16 цифр."},
        {"input": "1234", "expected_error": "Номер карты должен содержать 16 цифр."},
        {"input": 1234567890123, "expected_error": "Номер карты должен содержать 16 цифр."},
        {"input": "1234567890123", "expected_error": "Номер карты должен содержать 16 цифр."},
        {"input": 12345678901234567, "expected_error": "Номер карты должен содержать 16 цифр."},
        {"input": "12345678901234567", "expected_error": "Номер карты должен содержать 16 цифр."}
    ]


@pytest.fixture
def edge_case_card_numbers():
    """Фикстура с граничными случаями для номеров карт."""
    return [
        {"input": 0000000000000000, "expected": "0000 00** **** 0000"},
        {"input": "0000000000000000", "expected": "0000 00** **** 0000"},
        {"input": 9999999999999999, "expected": "9999 99** **** 9999"},
        {"input": "9999999999999999", "expected": "9999 99** **** 9999"}
    ]


@pytest.fixture
def valid_account_numbers():
    """Фикстура с валидными номерами счетов."""
    return [
        987654321,
        "987654321",
        12345678,
        "12345678",
        1234,
        "1234",
        12,
        "12",
        5,
        "5"
    ]


@pytest.fixture
def edge_case_account_numbers():
    """Фикстура с граничными случаями для номеров счетов."""
    return [
        {"input": 1234, "expected": "**1234"},
        {"input": "1234", "expected": "**1234"},
        {"input": 12, "expected": "**12"},
        {"input": "12", "expected": "**12"},
        {"input": 5, "expected": "**5"},
        {"input": "5", "expected": "**5"}
    ]


# Фикстуры для функции filter_by_state

@pytest.fixture
def data_with_multiple_states() -> List[Dict[str, Any]]:
    """Данные с разными статусами (EXECUTED, CANCELED, PENDING)."""
    return [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
        {'id': 777777777, 'state': 'PENDING', 'date': '2023-01-15T10:10:10.101010'}
    ]


@pytest.fixture
def data_empty() -> List[Dict[str, Any]]:
    """Пустой список данных."""
    return []


@pytest.fixture
def data_all_executed() -> List[Dict[str, Any]]:
    """Все элементы имеют статус EXECUTED."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': '2023-01-01T00:00:00.000000'},
        {'id': 2, 'state': 'EXECUTED', 'date': '2023-01-02T00:00:00.000000'}
    ]


@pytest.fixture
def data_missing_state_key() -> List[Dict[str, Any]]:
    """Элементы с отсутствующим ключом 'state'."""
    return [
        {'id': 1, 'date': '2023-01-01T00:00:00.000000'},  # нет state
        {'id': 2, 'state': 'EXECUTED', 'date': '2023-01-02T00:00:00.000000'},
        {'id': 3}  # нет ни state, ни date
    ]


@pytest.fixture
def data_non_existent_state() -> List[Dict[str, Any]]:
    """Данные, где нет элементов с указанным статусом."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': '2023-01-01T00:00:00.000000'},
        {'id': 2, 'state': 'CANCELED', 'date': '2023-01-02T00:00:00.000000'}
    ]


# Фикстуры для функции sort_by_date

@pytest.fixture
def data_various_dates() -> List[Dict[str, Any]]:
    """Разные даты для сортировки (с миллисекундами и без)."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': '2023-01-01T12:00:00'},
        {'id': 2, 'state': 'CANCELED', 'date': '2023-01-03T14:45:30.123456'},
        {'id': 3, 'state': 'PENDING', 'date': '2023-01-02T13:30:45'},
        {'id': 4, 'state': 'EXECUTED', 'date': '2022-12-31T23:59:59.999999'}
    ]


@pytest.fixture
def data_same_dates() -> List[Dict[str, Any]]:
    """Несколько элементов с одинаковой датой."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': '2023-01-01T12:00:00.000000'},
        {'id': 2, 'state': 'CANCELED', 'date': '2023-01-01T12:00:00.000000'},
        {'id': 3, 'state': 'PENDING', 'date': '2023-01-02T12:00:00.000000'}
    ]


@pytest.fixture
def data_single_item() -> List[Dict[str, Any]]:
    """Один элемент в списке."""
    return [{'id': 1, 'state': 'EXECUTED', 'date': '2023-01-01T12:00:00.000000'}]


@pytest.fixture
def data_invalid_dates() -> List[Dict[str, Any]]:
    """Даты в некорректном формате."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': 'invalid-date-format'},
        {'id': 2, 'state': 'CANCELED', 'date': '2023/01/01 12:00:00'}  # неверный разделитель
    ]


@pytest.fixture
def data_missing_date_key() -> List[Dict[str, Any]]:
    """Элементы без ключа 'date'."""
    return [
        {'id': 1, 'state': 'EXECUTED'},
        {'id': 2, 'state': 'CANCELED', 'date': '2023-01-01T12:00:00.000000'}
    ]


@pytest.fixture
def data_iso_formats() -> List[Dict[str, Any]]:
    """Различные варианты ISO‑формата дат."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': '2023-01-01'},  # только дата
        {'id': 2, 'state': 'CANCELED', 'date': '2023-01-02T12:00:00'},  # без миллисекунд
        {'id': 3, 'state': 'PENDING', 'date': '2023-01-03T13:30:45.123'},  # с миллисекундами
        {'id': 4, 'state': 'EXECUTED', 'date': '2023-01-04T14:45:50.123456'}  # полные миллисекунды
    ]


# Фикстура для теста widget
@pytest.fixture
def valid_card_data():
    """Фикстура с валидными данными для маскировки карт."""
    return [
        {
            "input": "Visa Platinum 7000792289606361",
            "expected": "Visa Platinum 7000 79** **** 6361"
        },
        {
            "input": "MasterCard 5412345678901234",
            "expected": "MasterCard 5412 34** **** 1234"
        },
        {
            "input": "American Express 3782822463100005",
            "expected": "American Express 3782 82** **** 0005"
        }
    ]


@pytest.fixture
def valid_account_data():
    """Фикстура с валидными данными для маскировки счетов."""
    return [
        {
            "input": "Счёт 98765432101234567890",
            "expected": "Счёт **7890"
        },
        {
            "input": "Накопительный счёт 123456789",
            "expected": "Накопительный счёт **89"
        },
        {
            "input": "Вклад 1234",
            "expected": "Вклад **34"
        }
    ]


@pytest.fixture
def valid_date_strings():
    """Фикстура с валидными строками дат в формате ISO."""
    return [
        {
            "input": "2024-03-11T02:26:18.671407",
            "expected": "11.03.2024"
        },
        {
            "input": "2022-01-01T00:00:00.000000",
            "expected": "01.01.2022"
        },
        {
            "input": "2023-12-25T15:30:45.123456",
            "expected": "25.12.2023"
        }
    ]


@pytest.fixture
def invalid_date_formats():
    """Фикстура с некорректными форматами дат."""
    return [
        "2024/03/11 02:26:18",
        "11-03-2024T02:26:18",
        "invalid-date-format",
        "",
        "2024-13-01T00:00:00"  # некорректный месяц
    ]
