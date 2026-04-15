import os
import sys
import pytest
import pandas as pd
from unittest.mock import mock_open, patch
from file_reader import read_csv_transactions, read_excel_transactions

# Исправляем импорт пути
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_file_exists():
    with patch('file_reader.os.path.exists') as mock:
        yield mock


@pytest.fixture
def mock_csv_open():
    with patch('builtins.open', mock_open()) as mock:
        yield mock


class TestCSVReader:
    @pytest.mark.parametrize("csv_content,expected_result", [
        (
                "id;amount;currency\n1;1000;RUB\n2;2000;USD",
                [
                    {'id': '1', 'amount': '1000', 'currency': 'RUB'},
                    {'id': '2', 'amount': '2000', 'currency': 'USD'}
                ]
        ),
        (
                " id ; amount ; currency \n 1 ; 1000 ; RUB \n 2 ; 2000 ; USD ",
                [
                    {'id': '1', 'amount': '1000', 'currency': 'RUB'},
                    {'id': '2', 'amount': '2000', 'currency': 'USD'}
                ]
        )
    ])
    def test_read_csv_success(self, mock_file_exists, mock_csv_open, csv_content, expected_result):
        """Тест успешного чтения CSV‑файла с разными форматами данных."""
        mock_file_exists.return_value = True

        # ПРАВИЛЬНАЯ настройка мока: передаём данные через read_data
        mock_csv_open.side_effect = mock_open(read_data=csv_content)

        result = read_csv_transactions('transactions.csv')

        # Проверяем, что open был вызван с правильными параметрами
        mock_csv_open.assert_called_once_with('transactions.csv', 'r', encoding='utf-8')
        assert len(result) == len(expected_result)
        for i, row in enumerate(expected_result):
            assert result[i] == row

    def test_read_csv_empty_file(self, mock_file_exists, mock_csv_open):
        """Тест чтения пустого CSV‑файла."""
        mock_file_exists.return_value = True
        mock_csv_open.side_effect = mock_open(read_data="")

        result = read_csv_transactions('empty.csv')
        assert result == []

    def test_csv_headers_only(self, mock_file_exists, mock_csv_open):
        """Тест CSV только с заголовками."""
        mock_file_exists.return_value = True
        csv_content = "id;amount;currency\n"
        mock_csv_open.side_effect = mock_open(read_data=csv_content)

        result = read_csv_transactions('headers_only.csv')
        assert result == []

    def test_csv_file_not_found(self, mock_file_exists):
        """Тест на отсутствие файла."""
        mock_file_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            read_csv_transactions('nonexistent.csv')

    def test_csv_unicode_error(self, mock_file_exists, mock_csv_open):
        """Тест на ошибку декодирования UTF‑8."""
        mock_file_exists.return_value = True
        # Имитируем UnicodeDecodeError
        mock_csv_open.side_effect = UnicodeDecodeError('utf-8', b'\x80', 0, 1, 'invalid start byte')

        with pytest.raises(UnicodeDecodeError):
            read_csv_transactions('bad_encoding.csv')


class TestExcelReader:

    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_read_excel_basic_call(self, mock_read_excel, mock_exists):
        """Минимальный тест на вызов read_excel."""
        mock_exists.return_value = True
        mock_read_excel.return_value = pd.DataFrame({'date': ['2023-01-01']})

        read_excel_transactions('simple.xlsx')
        assert mock_read_excel.called, "read_excel не был вызван"

    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_excel_large_file(self, mock_read_excel, mock_exists):
        """Тест производительности на большом файле (10 000 записей)."""
        mock_exists.return_value = True

        # Создаём большой DataFrame для теста
        large_data = []
        for i in range(10000):
            large_data.append({
                'date': f'2023-01-{i + 1:02d}',
                'description': f'Payment {i + 1}',
                'amount': float(i * 10),
                'currency_code': 'RUB',
                'from': f'Account {i}',
                'to': f'Target {i}',
                'state': 'completed' if i % 2 == 0 else 'pending'
            })
        test_data = pd.DataFrame(large_data)
        mock_read_excel.return_value = test_data

        result = read_excel_transactions('large_file.xlsx')
        assert len(result) == 10000
        # Проверяем несколько случайных записей
        assert result[0]['description'] == 'Payment 1'
        assert result[9999]['amount'] == '99990.0'

    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_excel_duplicate_rows(self, mock_read_excel, mock_exists):
        """Тест на обработку дублирующихся строк."""
        mock_exists.return_value = True

        test_data = pd.DataFrame([
            {'date': '2023-01-01', 'description': 'Duplicate', 'amount': 100,
             'currency_code': 'RUB', 'from': 'Source', 'to': 'Target', 'state': 'completed'},
            {'date': '2023-01-01', 'description': 'Duplicate', 'amount': 100,
             'currency_code': 'RUB', 'from': 'Source', 'to': 'Target', 'state': 'completed'}
        ])
        mock_read_excel.return_value = test_data

        result = read_excel_transactions('duplicate_rows.xlsx')
        # Дубликаты должны сохраняться — это ответственность пользователя
        assert len(result) == 2
        assert result[0] == result[1]

    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_excel_empty_sheet(self, mock_read_excel, mock_exists):
        """Тест пустого Excel‑листа (нет данных, только заголовки)."""
        mock_exists.return_value = True
        empty_df = pd.DataFrame(columns=['date', 'description', 'amount',
                                         'currency_code', 'from', 'to', 'state'])
        mock_read_excel.return_value = empty_df

        result = read_excel_transactions('empty_sheet.xlsx')
        assert result == []

    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_excel_parser_error(self, mock_read_excel, mock_exists):
        """Тест обработки ошибки парсинга Excel (повреждённый файл)."""
        mock_exists.return_value = True
        mock_read_excel.side_effect = pd.errors.ParserError("Ошибка чтения Excel")

        with pytest.raises(pd.errors.ParserError) as exc_info:
            read_excel_transactions('corrupted.xlsx')
        assert "Ошибка чтения Excel" in str(exc_info.value)

    @patch('file_reader.os.path.exists')
    def test_excel_file_not_found(self, mock_exists):
        """Тест на отсутствие Excel‑файла."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            read_excel_transactions('nonexistent.xlsx')
