import pytest
from ..src.masks import get_mask_card_number, get_mask_account


def test_get_mask_card_number_int(valid_card_numbers):
    # Тестируем целое число
    result = get_mask_card_number(valid_card_numbers[0])
    assert result == "1234 56** **** 3456"


def test_get_mask_card_number_string(valid_card_numbers):
    # Тестируем строку
    result = get_mask_card_number(valid_card_numbers[1])
    assert result == "1234 56** **** 3456"


def test_get_mask_card_number_valid(valid_card_numbers):
    """Тест с валидными номерами карт."""
    for card in valid_card_numbers:
        result = get_mask_card_number(card)
        # Проверяем формат маски: 4 цифры + пробел + 2 цифры + ** + пробел + **** + пробел + 4 цифры
        assert len(result) == 19
        assert result.count('*') == 6
        assert result[4] == ' ' and result[9] == ' ' and result[14] == ' '
        # Первые и последние 4 цифры должны совпадать с оригиналом
        card_str = str(card)
        assert result[:4] == card_str[:4]
        assert result[-4:] == card_str[-4:]


def test_get_mask_card_number_invalid_lengths(invalid_card_lengths):
    """Тест с номерами карт некорректной длины."""
    for case in invalid_card_lengths:
        with pytest.raises(ValueError) as exc_info:
            get_mask_card_number(case["input"])
        assert case["expected_error"] in str(exc_info.value)


def test_get_mask_card_number_valid_string():
    """Тест с корректным номером карты в виде строки."""
    result = get_mask_card_number("1234567890123456")
    assert result == "1234 56** **** 3456"


def test_get_mask_card_number_short_number():
    """Тест с номером карты меньше 16 цифр."""
    with pytest.raises(ValueError) as exc_info:
        get_mask_card_number("1234")
    assert "Номер карты должен содержать 16 цифр" in str(exc_info.value)


def test_get_mask_card_number_long_number():
    """Тест с номером карты больше 16 цифр."""
    with pytest.raises(ValueError) as exc_info:
        get_mask_card_number("12345678901234567")
    assert "Номер карты должен содержать 16 цифр" in str(exc_info.value)


# def test_get_mask_card_number_none_input():
#     """Тест с None в качестве входных данных."""
#     with pytest.raises(TypeError) as exc_info:
#         get_mask_card_number(None)
#     assert "Номер карты должен быть числом или строкой" in str(exc_info.value)


def test_get_mask_card_number_empty_string():
    """Тест с пустой строкой."""
    with pytest.raises(ValueError) as exc_info:
        get_mask_card_number("")
    assert "Номер карты должен содержать 16 цифр" in str(exc_info.value)


def test_get_mask_card_number_leading_zeros():
    """Тест с ведущими нулями в номере карты."""
    result = get_mask_card_number("0000123456789012")
    assert result == "0000 12** **** 9012"


def test_get_mask_card_number_all_zeros():
    """Тест с номером карты из всех нулей."""
    result = get_mask_card_number("0000000000000000")
    assert result == "0000 00** **** 0000"


def test_get_mask_account_valid_int():
    """Тест с корректным номером счёта в виде целого числа."""
    result = get_mask_account(987654321)
    assert result == "**4321"


def test_get_mask_account_valid_string():
    """Тест с корректным номером счёта в виде строки."""
    result = get_mask_account("12345678")
    assert result == "**5678"


def test_get_mask_account_short_number():
    """Тест с номером счёта меньше 4 цифр."""
    result = get_mask_account("12")
    assert result == "**12"


def test_get_mask_account_exactly_4_digits():
    """Тест с номером счёта ровно из 4 цифр."""
    result = get_mask_account("1234")
    assert result == "**1234"


def test_get_mask_account_empty_string():
    """Тест с пустой строкой."""
    result = get_mask_account("")
    assert result == "**"


def test_get_mask_account_leading_zeros():
    """Тест с ведущими нулями в номере счёта."""
    result = get_mask_account("00001234")
    assert result == "**1234"


def test_get_mask_account_all_zeros():
    """Тест с номером счёта из всех нулей."""
    result = get_mask_account("0000")
    assert result == "**0000"


def test_get_mask_account_long_number():
    """Тест с длинным номером счёта (больше 4 цифр)."""
    result = get_mask_account("9876543210")
    assert result == "**3210"


def test_get_mask_account_number_edge_cases(edge_case_account_numbers):
    """Тест граничных случаев для номеров счетов."""
    for case in edge_case_account_numbers:
        result = get_mask_account(case["input"])
        assert result == case["expected"]
