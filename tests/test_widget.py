import pytest
from ..src.widget import mask_account_card, get_date


def test_mask_account_card_american_express():
    """Специальный тест для American Express (15‑значный номер)."""
    result = mask_account_card("American Express 3782822463100005")
    assert result == "American Express 3782 82** **** 0005"


def test_mask_account_card_valid_cards(valid_card_data):
    """
    Тест маскировки корректных номеров карт.

    Проверяет, что функция корректно маскирует номера различных типов карт,
    сохраняя название типа карты и применяя маску к номеру.
    """
    for case in valid_card_data:
        result = mask_account_card(case["input"])
        assert result == case["expected"]


def test_get_date_valid_iso_formats(valid_date_strings):
    """
    Тест преобразования дат в стандартном ISO‑формате.

    Проверяет обработку различных валидных дат в формате ISO 8601
    с миллисекундами и без них.
    """
    for case in valid_date_strings:
        result = get_date(case["input"])
        assert result == case["expected"]


def test_get_date_invalid_formats(invalid_date_formats):
    """
    Тест с некорректными форматами дат.

    Проверяет, что функция выбрасывает ValueError для некорректных форматов дат.
    """
    for date_string in invalid_date_formats:
        with pytest.raises(ValueError):
            get_date(date_string)


def test_mask_account_card_valid_card():
    """Тест маскировки корректного номера карты."""
    result = mask_account_card("Visa Platinum 7000792289606361")
    assert result == "Visa Platinum 7000 79** **** 6361"


def test_mask_account_card_valid_account():
    """Тест маскировки корректного номера счёта."""
    result = mask_account_card("Счёт 98765432101234567890")
    assert result == "Счёт **7890"


# def test_get_date_valid_iso_format():
#     """Тест преобразования даты в стандартном ISO‑формате."""
#     result = get_date("2024-03-11T02:26:18.671407")
#     assert result == "11.03.2024"


def test_get_date_valid_iso_format():
    """Тест преобразования даты в стандартном ISO‑формате."""
    result = get_date("2024-03-11T02:26:18.671407")
    assert result == "11.03.2024"


def test_get_date_date_with_zero_milliseconds():
    """Тест даты с нулевыми миллисекундами."""
    result = get_date("2022-01-01T00:00:00.000000")
    assert result == "01.01.2022"


def test_get_date_different_separators():
    """Тест дат с разными разделителями (если функция поддерживает)."""
    # Если функция должна обрабатывать разные форматы
    try:
        result = get_date("2024/03/11 02:26:18")
        assert result == "11.03.2024"
    except ValueError:
        # Если не поддерживает — ожидаем ошибку
        pass
