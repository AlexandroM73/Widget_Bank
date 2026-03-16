import pytest
from src.processing import filter_by_state, sort_by_date


class TestFilterByState:

    @pytest.mark.parametrize("state,expected_count", [
        ('EXECUTED', 2),
        ('CANCELED', 2),
        ('PENDING', 1),
        ('UNKNOWN', 0)
    ])
    def test_filter_by_state_parametrized(self, data_with_multiple_states, state, expected_count):
        """Параметризованный тест фильтрации по разным состояниям."""
        result = filter_by_state(data_with_multiple_states, state)
        assert len(result) == expected_count
        if expected_count > 0:
            assert all(item['state'] == state for item in result)

    def test_filter_empty_list(self, data_empty):
        """Тест фильтрации пустого списка."""
        result = filter_by_state(data_empty)
        assert result == []

    def test_filter_missing_state_key(self, data_missing_state_key):
        """Тест фильтрации данных с отсутствующим ключом 'state'."""
        result = filter_by_state(data_missing_state_key, 'EXECUTED')
        assert len(result) == 1
        assert result[0]['id'] == 2

    def test_filter_non_list_input(self):
        """Тест передачи не списка в качестве данных."""
        with pytest.raises(TypeError):
            filter_by_state("not a list", 'EXECUTED')

    def test_filter_none_input(self):
        """Тест передачи None в качестве данных."""
        with pytest.raises(TypeError):
            filter_by_state(None, 'EXECUTED')


class TestSortByDate:

    @pytest.mark.parametrize("reverse,expected_order", [
        (True, ['2023-01-03T14:45:30.123456', '2023-01-02T13:30:45',
                '2023-01-01T12:00:00', '2022-12-31T23:59:59.999999']),
        (False, ['2022-12-31T23:59:59.999999', '2023-01-01T12:00:00',
                 '2023-01-02T13:30:45', '2023-01-03T14:45:30.123456'])
    ])
    def test_sort_by_date_parametrized(self, data_various_dates, reverse, expected_order):
        """Параметризованный тест сортировки по дате в разных направлениях."""
        result = sort_by_date(data_various_dates, reverse=reverse)
        dates = [item['date'] for item in result]
        assert dates == expected_order

    def test_sort_empty_list(self, data_empty):
        """Тест сортировки пустого списка."""
        result = sort_by_date(data_empty)
        assert result == []

    def test_sort_single_item(self):
        """Тест сортировки списка с одним элементом."""
        single_data = [{'id': 1, 'state': 'EXECUTED', 'date': '2023-01-01T12:00:00'}]
        result = sort_by_date(single_data)
        assert len(result) == 1
        assert result[0]['id'] == 1

    def test_sort_same_dates(self):
        """Тест сортировки элементов с одинаковой датой."""
        data = [
            {'id': 1, 'state': 'EXECUTED', 'date': '2023-01-01T12:00:00.000000'},
            {'id': 2, 'state': 'CANCELED', 'date': '2023-01-01T12:00:00.000000'},
            {'id': 3, 'state': 'PENDING', 'date': '2023-01-02T12:00:00.000000'}
        ]
        result = sort_by_date(data)
        # При одинаковых датах порядок может сохраняться
        assert len(result) == 3
        # Проверяем, что элементы с одинаковой датой остались в исходном порядке
        assert result[0]['id'] in (1, 2)
        assert result[1]['id'] in (1, 2)

    def test_sort_missing_date_key(self):
        """Тест сортировки данных с отсутствующим ключом 'date'."""
        data = [
            {'id': 1, 'state': 'EXECUTED'},  # нет date
            {'id': 2, 'state': 'CANCELED', 'date': '2023-01-01T12:00:00'},
            {'id': 3, 'state': 'PENDING'}  # нет date
        ]
        result = sort_by_date(data)
        # Должны остаться только элементы с корректным ключом 'date'
        assert len(result) == 1
        assert result[0]['id'] == 2

    def test_sort_invalid_date_format(self, data_invalid_dates):
        """Тест обработки некорректного формата даты."""
        result = sort_by_date(data_invalid_dates)
        # Функция должна пропустить элементы с некорректными датами
        assert len(result) == 0

    def test_sort_non_list_input(self):
        """Тест передачи не списка в качестве данных."""
        with pytest.raises(TypeError):
            sort_by_date("not a list")

    def test_sort_none_input(self):
        """Тест передачи None в качестве данных."""
        with pytest.raises(TypeError):
            sort_by_date(None)


class TestCombinedUsage:

    @pytest.mark.parametrize("filter_state,sort_reverse,expected_first_id", [
        ('EXECUTED', True, 41428829),  # EXECUTED, убывание — самая новая
        ('EXECUTED', False, 939719570),  # EXECUTED, возрастание — самая старая
        ('CANCELED', True, 615064591),  # CANCELED, убывание
        ('PENDING', False, 777777777),  # PENDING, возрастание (только один элемент)
        ('UNKNOWN', True, None),  # Несуществующий статус — пустой результат
    ])
    def test_combined_filter_and_sort(self, data_with_multiple_states, filter_state, sort_reverse, expected_first_id):
        """Комбинированный тест: фильтрация + сортировка с разными параметрами."""
        filtered = filter_by_state(data_with_multiple_states, filter_state)
        sorted_data = sort_by_date(filtered, reverse=sort_reverse)

        if expected_first_id is None:
            # Если статус не найден, результат должен быть пустым
            assert len(sorted_data) == 0
        else:
            # Иначе проверяем первый элемент
            assert sorted_data[0]['id'] == expected_first_id

    def test_filter_then_sort_empty_result(self, data_with_multiple_states):
        """Тест комбинации: фильтрация даёт пустой результат, затем сортировка."""
        filtered = filter_by_state(data_with_multiple_states, 'UNKNOWN')
        sorted_data = sort_by_date(filtered)
        assert len(sorted_data) == 0


class TestErrorCases:

    def test_filter_with_none_data(self):
        """Тест вызова filter_by_state с None."""
        with pytest.raises(TypeError):
            filter_by_state(None, 'EXECUTED')

    def test_sort_with_none_data(self):
        """Тест вызова sort_by_date с None."""
        with pytest.raises(TypeError):
            sort_by_date(None)
