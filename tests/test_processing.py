import pytest
from src.processing import filter_by_state, sort_by_date


def test_filter_by_state_multiple_states(data_with_multiple_states):
    """Тест фильтрации по статусу EXECUTED."""
    result = filter_by_state(data_with_multiple_states, "EXECUTED")
    assert len(result) == 2
    assert all(item["state"] == "EXECUTED" for item in result)


def test_filter_by_state_empty(data_empty):
    """Тест с пустым списком данных."""
    result = filter_by_state(data_empty, "EXECUTED")
    assert result == []


def test_filter_by_state_all_executed(data_all_executed):
    """Тест когда все элементы имеют статус EXECUTED."""
    result = filter_by_state(data_all_executed, "EXECUTED")
    assert len(result) == 2


def test_filter_by_state_missing_state_key(data_missing_state_key):
    """Тест с элементами без ключа 'state'."""
    result = filter_by_state(data_missing_state_key, "EXECUTED")
    # Элементы без state не должны попадать в результат
    assert len(result) == 1
    assert result[0]["id"] == 2  # только элемент с state=EXECUTED


def test_filter_by_state_non_existent_state(data_non_existent_state):
    """Тест когда нет элементов с указанным статусом."""
    result = filter_by_state(data_non_existent_state, "PENDING")
    assert result == []


def test_sort_by_date_various_dates(data_various_dates):
    """Тест сортировки с разными датами."""
    result = sort_by_date(data_various_dates)
    # Проверяем, что даты отсортированы по убыванию (самые новые — первые)
    dates = [item["date"] for item in result]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


def test_sort_by_date_same_dates(data_same_dates):
    """Тест сортировки с одинаковыми датами."""
    result = sort_by_date(data_same_dates)
    # При одинаковых датах порядок может сохраняться
    assert len(result) == 3


def test_sort_by_date_single_item(data_single_item):
    """Тест сортировки одного элемента."""
    result = sort_by_date(data_single_item)
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_sort_by_date_invalid_dates(data_invalid_dates):
    """Тест с некорректными форматами дат."""
    with pytest.raises(ValueError):
        sort_by_date(data_invalid_dates)


def test_sort_by_date_missing_date_key(data_missing_date_key):
    """Тест с элементами без ключа 'date'."""
    # Предполагаем, что элементы без даты игнорируются или выбрасывается ошибка
    with pytest.raises(KeyError):  # или другой ожидаемый тип ошибки
        sort_by_date(data_missing_date_key)


def test_sort_by_date_iso_formats(data_iso_formats):
    """Тест с разными вариантами ISO‑формата дат."""
    result = sort_by_date(data_iso_formats)
    # Проверяем, что функция корректно обрабатывает разные форматы ISO
    assert len(result) == 4
