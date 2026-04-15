import pytest
from typing import List, Dict, Any
from count_module import process_bank_operations
from search_module import process_bank_search


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {'description': 'Покупка в супермаркете "Пятёрочка"', 'amount': 1500, 'date': '2023-01-01'},
        {'description': 'Обед в ресторане "Итальяно"', 'amount': 2500, 'date': '2023-01-02'},
        {'description': 'Оплата проезда в метро', 'amount': 50, 'date': '2023-01-03'},
        {'description': 'Лекарства в аптеке "Здоровье"', 'amount': 800, 'date': '2023-01-04'},
        {'description': 'Перевод другу Ивану', 'amount': 3000, 'date': '2023-01-05'},
        {'description': 'Супермаркет "Магнит" — продукты', 'amount': 2000, 'date': '2023-01-06'},
        {'description': 'Ужин в ресторане "Француз"', 'amount': 3500, 'date': '2023-01-07'},
        {'description': 'Билеты на автобус', 'amount': 100, 'date': '2023-01-08'},
        {'description': 'Витамины в аптеке', 'amount': 400, 'date': '2023-01-09'},
        {'description': 'Перевод на карту', 'amount': 5000, 'date': '2023-01-10'},
        {'description': 'Покупка на сайте example.com', 'amount': 700, 'date': '2023-01-11'},
        {'description': 'Скидка 20% в магазине', 'amount': 600, 'date': '2023-01-12'},
    ]


@pytest.fixture
def sample_categories() -> List[str]:
    return ['супермаркет', 'ресторан', 'транспорт', 'аптека', 'перевод']


@pytest.fixture
def edge_case_transactions() -> List[Dict[str, Any]]:
    return [
        {'description': ''},
        {'amount': 1000, 'date': '2023-01-01'},  # нет description
        {'description': '   '},  # пробелы
    ]


# ТЕСТЫ ДЛЯ process_bank_operations
def test_operations_empty_data_list(sample_categories):
    result = process_bank_operations([], sample_categories)
    expected = {category: 0 for category in sample_categories}
    assert result == expected


def test_operations_empty_categories_list(sample_transactions):
    result = process_bank_operations(sample_transactions, [])
    assert result == {}


def test_operations_word_boundaries():
    data = [
        {'description': 'Супермаркет'},
        {'description': 'Супермаркеты'},
        {'description': 'В супермаркете'},
        {'description': 'Супермаркетный'},
    ]
    categories = ['супермаркет']
    result = process_bank_operations(data, categories)
    # Ожидаем 1 совпадение: только 'Супермаркет' (строгое соответствие с границей слова)
    assert result['супермаркет'] == 1


def test_operations_with_missing_or_empty_descriptions(sample_categories, edge_case_transactions, sample_transactions):
    all_data = sample_transactions + edge_case_transactions
    result = process_bank_operations(all_data, sample_categories)
    base_result = process_bank_operations(sample_transactions, sample_categories)
    for category in sample_categories:
        assert result[category] == base_result[category]


# ТЕСТЫ ДЛЯ process_bank_search
def test_search_empty_search_string(sample_transactions):
    """Тест: пустая строка поиска должна возвращать пустой список."""
    result = process_bank_search(sample_transactions, '')
    assert result == []


def test_search_empty_data_list():
    """Тест: пустой список данных должен возвращать пустой список."""
    result = process_bank_search([], 'супермаркет')
    assert result == []


def test_search_exact_match(sample_transactions):
    """Тест: точное совпадение строки в описании."""
    result = process_bank_search(sample_transactions, 'супермаркет')
    expected_descriptions = ['Покупка в супермаркете "Пятёрочка"', 'Супермаркет "Магнит" — продукты']
    result_descriptions = [t['description'] for t in result]
    assert len(result) == 2
    for desc in expected_descriptions:
        assert desc in result_descriptions


def test_search_case_insensitive(sample_transactions):
    """Тест: поиск должен быть нечувствителен к регистру."""
    result1 = process_bank_search(sample_transactions, 'СУПЕРМАРКЕТ')
    result2 = process_bank_search(sample_transactions, 'супермаркет')
    assert len(result1) == len(result2) == 2


def test_search_partial_match(sample_transactions):
    """Тест: частичное совпадение строки в описании."""
    result = process_bank_search(sample_transactions, 'аптек')
    expected_descriptions = ['Лекарства в аптеке "Здоровье"', 'Витамины в аптеке']
    result_descriptions = [t['description'] for t in result]
    for desc in expected_descriptions:
        assert desc in result_descriptions


def test_search_special_characters(sample_transactions):
    """Тест: специальные символы в строке поиска экранируются."""
    # Ищем строку с точкой
    result1 = process_bank_search(sample_transactions, 'example.com')
    assert len(result1) == 1
    assert 'example.com' in result1[0]['description']

    # Ищем строку со скобками
    result2 = process_bank_search(sample_transactions, '20%')
    assert len(result2) == 1
    assert '20%' in result2[0]['description']


def test_search_no_matches(sample_transactions):
    """Тест: если совпадений нет, возвращается пустой список."""
    result = process_bank_search(sample_transactions, 'не существующая строка')
    assert result == []


def test_search_multiple_fields(sample_transactions):
    """Тест: транзакции с дополнительными полями (функция должна возвращать полные словари)."""
    result = process_bank_search(sample_transactions, 'ресторан')

    # Проверяем, что вернулись полные транзакции со всеми полями
    assert len(result) == 2  # Ожидаем две транзакции с упоминанием ресторана

    for transaction in result:
        # Проверяем наличие всех полей из исходной транзакции
        assert 'description' in transaction
        assert 'amount' in transaction
        assert 'date' in transaction

        # Проверяем корректность данных
        assert isinstance(transaction['amount'], int)
        assert isinstance(transaction['date'], str)
        assert 'ресторан' in transaction['description'].lower()

    # Конкретная проверка значений
    restaurant_descriptions = [t['description'] for t in result]
    expected_descriptions = [
        'Обед в ресторане "Итальяно"',
        'Ужин в ресторане "Француз"'
    ]

    for desc in expected_descriptions:
        assert desc in restaurant_descriptions


def test_search_whitespace_handling(sample_transactions):
    """Тест: обработка пробелов в строке поиска."""
    data = [
        {'description': '  Покупка в супермаркете  ', 'amount': 1500},
        {'description': 'Оплата ресторана', 'amount': 2500},
    ]
    result = process_bank_search(data, 'Покупка в супермаркете')
    assert len(result) == 1
    assert result[0]['description'] == '  Покупка в супермаркете  '


def test_search_with_spaces(sample_transactions):
    """Тест: строка поиска с пробелами."""
    result = process_bank_search(sample_transactions, 'Покупка в супермаркете')
    assert len(result) == 1
    assert 'Покупка в супермаркете "Пятёрочка"' in [t['description'] for t in result]


def test_search_missing_description_field(edge_case_transactions):
    """Тест: транзакция без поля description должна пропускаться."""
    # Добавляем транзакцию с description к edge_case данным
    test_data = edge_case_transactions + [
        {'description': 'Покупка в супермаркете', 'amount': 1000}
    ]

    result = process_bank_search(test_data, 'супермаркет')
    # Должна найтись только транзакция с description
    assert len(result) == 1
    assert result[0]['description'] == 'Покупка в супермаркете'


def test_search_empty_description(edge_case_transactions):
    """Тест: пустая строка в description не должна находить совпадений."""
    result = process_bank_search(edge_case_transactions, 'что‑то')
    assert len(result) == 0


def test_search_special_regex_characters():
    """Тест: поиск строк, которые являются специальными символами в regex."""
    data = [
        {'description': 'Сумма: 100.50 руб.', 'amount': 10050},
        {'description': 'Код: A*B*C', 'amount': 0},
        {'description': 'Диапазон: [1-10]', 'amount': 0},
    ]

    # Ищем точку как обычный символ
    result1 = process_bank_search(data, '100.50')
    assert len(result1) == 1
    assert '100.50' in result1[0]['description']

    # Ищем звёздочку как обычный символ
    result2 = process_bank_search(data, 'A*B*C')
    assert len(result2) == 1
    assert 'A*B*C' in result2[0]['description']

    # Ищем квадратные скобки как обычные символы
    result3 = process_bank_search(data, '[1-10]')
    assert len(result3) == 1
    assert '[1-10]' in result3[0]['description']
