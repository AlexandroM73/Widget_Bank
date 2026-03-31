import os
import sys
import pytest
import pandas as pd
from unittest.mock import mock_open, patch
from file_reader import read_csv_transactions, read_excel_transactions

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestCSVReader:
    class TestCSVReader:
        @pytest.mark.parametrize('mock_csv_file', [
            "id,amount,currency\n1,1000,RUB\n2,2000,USD"
        ], indirect=True)
        def test_read_csv_success(self, mock_file_exists, mock_csv_file):
            mock_file_exists.return_value = True
            result = read_csv_transactions('transactions.csv')
            mock_csv_file.assert_called_once_with('transactions.csv', 'r', encoding='utf-8')
            assert len(result) == 2
            assert result[0] == {'id': '1', 'amount': '1000', 'currency': 'RUB'}
            assert result[1] == {'id': '2', 'amount': '2000', 'currency': 'USD'}

        @pytest.mark.parametrize('mock_csv_file', [" id , amount , currency \n 1 , 1000 , RUB "], indirect=True)
        def test_csv_with_extra_spaces(self, mock_file_exists, mock_csv_file):
            mock_file_exists.return_value = True
            result = read_csv_transactions('spaces.csv')
            assert len(result) == 1
            assert result[0]['id'].strip() == '1'
            assert result[0]['amount'].strip() == '1000'
            assert result[0]['currency'].strip() == 'RUB'

    def test_read_csv_empty_file(self, mock_file_exists, mock_builtins_open, empty_csv_data):
        """Тест чтения пустого CSV‑файла."""
        mock_file_exists.return_value = True
        mock_builtins_open.side_effect = mock_open(read_data=empty_csv_data).side_effect
        result = read_csv_transactions('empty.csv')
        assert result == []

    def test_read_csv_headers_only(self, mock_file_exists, mock_builtins_open, headers_only_csv_data):
        """Тест CSV только с заголовками."""
        mock_file_exists.return_value = True
        mock_builtins_open.side_effect = mock_open(read_data=headers_only_csv_data).side_effect
        result = read_csv_transactions('headers_only.csv')
        assert result == []

    def test_csv_file_not_found(self, mock_file_exists):
        """Тест на отсутствие файла."""
        mock_file_exists.return_value = False
        with pytest.raises(FileNotFoundError):
            read_csv_transactions('nonexistent.csv')

    def test_csv_permission_error(self, mock_file_exists, mock_builtins_open):
        """Тест на ошибку доступа к CSV‑файлу."""
        mock_file_exists.return_value = True
        mock_builtins_open.side_effect = PermissionError("Permission denied")
        with pytest.raises(PermissionError):
            read_csv_transactions('restricted.csv')


class TestExcelReader:
    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_read_excel_success(self, mock_read_excel, mock_exists):
        """Тест успешного чтения Excel с использованием Mock."""
        mock_exists.return_value = True
        test_data = pd.DataFrame({
            'id': [1, 2],
            'amount': [1000, 2000],
            'currency': ['RUB', 'USD']
        })
        mock_read_excel.return_value = test_data
        result = read_excel_transactions('transactions_excel.xlsx')
        mock_read_excel.assert_called_once_with('transactions_excel.xlsx', sheet_name=0)
        mock_exists.assert_called_once_with('transactions_excel.xlsx')
        assert len(result) == 2
        assert result[0] == {'id': '1', 'amount': '1000', 'currency': 'RUB'}

    @patch('file_reader.os.path.exists')
    def test_excel_invalid_extension(self, mock_exists):
        """Тест на файл с неверным расширением."""
        mock_exists.return_value = True
        with pytest.raises(ValueError) as exc_info:
            read_excel_transactions('document.xls')
        assert "Ожидался файл .xlsx" in str(exc_info.value)

    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_excel_multiple_sheets(self, mock_read_excel, mock_exists):
        """Тест чтения Excel с несколькими листами (должен читать первый)."""
        mock_exists.return_value = True

        test_data = pd.DataFrame({
            'id': [1, 2],
            'amount': [500, 1500],
            'currency': ['EUR', 'GBP']
        })
        mock_read_excel.return_value = test_data

        result = read_excel_transactions('multiple_sheets.xlsx')

        # Проверяем вызовы
        mock_read_excel.assert_called_once_with('multiple_sheets.xlsx', sheet_name=0)
        mock_exists.assert_called_once_with('multiple_sheets.xlsx')

        # Проверяем результат
        assert len(result) == 2
        assert result[0] == {'id': '1', 'amount': '500', 'currency': 'EUR'}
        assert result[1] == {'id': '2', 'amount': '1500', 'currency': 'GBP'}

    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_excel_empty_data(self, mock_read_excel, mock_exists):
        """Тест на Excel с пустыми данными (пустой DataFrame)."""
        mock_exists.return_value = True

        empty_df = pd.DataFrame()
        mock_read_excel.return_value = empty_df

        result = read_excel_transactions('empty_excel.xlsx')

        # Проверяем вызовы
        mock_read_excel.assert_called_once_with('empty_excel.xlsx', sheet_name=0)
        mock_exists.assert_called_once_with('empty_excel.xlsx')

        # Проверяем результат: функция должна вернуть пустой список для пустого DataFrame
        assert isinstance(result, list), "Результат должен быть списком"
        assert len(result) == 0, "Список должен быть пустым для пустого Excel‑файла"
        assert result == [], "Результат должен точно совпадать с пустым списком"

    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_excel_with_nan_values(self, mock_read_excel, mock_exists):
        """Тест Excel с NaN‑значениями (должны заменяться на None)."""
        mock_exists.return_value = True

        # Создаём DataFrame с NaN‑значениями
        test_data = pd.DataFrame({
            'id': [1, None],
            'amount': [1000, 2000],
            'currency': ['RUB', None]
        })
        mock_read_excel.return_value = test_data

        result = read_excel_transactions('nan_data.xlsx')

        # Проверяем вызовы
        mock_read_excel.assert_called_once_with('nan_data.xlsx', sheet_name=0)
        mock_exists.assert_called_once_with('nan_data.xlsx')

        # Проверяем результат — NaN должны стать None
        assert len(result) == 2
        assert result[0] == {'id': '1', 'amount': '1000', 'currency': 'RUB'}
        assert result[1] == {'id': None, 'amount': '2000', 'currency': None}

    @patch('file_reader.os.path.exists')
    @patch('pandas.read_excel')
    def test_excel_single_row(self, mock_read_excel, mock_exists):
        """Тест Excel с одной строкой данных."""
        mock_exists.return_value = True

        test_data = pd.DataFrame({
            'id': [999],
            'amount': [9999],
            'currency': ['JPY']
        })
        mock_read_excel.return_value = test_data

        result = read_excel_transactions('single_row.xlsx')

        # Проверяем вызовы
        mock_read_excel.assert_called_once_with('single_row.xlsx', sheet_name=0)
        mock_exists.assert_called_once_with('single_row.xlsx')

        # Проверяем результат
        assert len(result) == 1
        assert result[0] == {'id': '999', 'amount': '9999', 'currency': 'JPY'}
