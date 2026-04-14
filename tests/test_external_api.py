import sys
import os
import pytest
from unittest.mock import patch, Mock
from external_api import convert_to_rubles
import requests

# Добавляем путь к src в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_path)


class TestConvertToRubles:

    @patch('external_api.requests.get')
    def test_convert_usd_to_rub_success(self, mock_get):
        """Тест успешной конвертации USD → RUB: result содержит готовую сумму."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 4500.0}
        mock_get.return_value = mock_response

        transaction = {"amount": 50.0, "currency": "USD"}
        result = convert_to_rubles(transaction)

        assert result == 4500.0

        expected_url = os.getenv("API_BASE_URL")
        expected_headers = {"apikey": os.getenv("API_KEY")}
        expected_params = {"base": "USD", "symbols": "RUB"}

        mock_get.assert_called_once_with(
            expected_url,
            headers=expected_headers,
            params=expected_params,
            timeout=10
        )

    @patch('external_api.requests.get')
    def test_convert_eur_to_rub_success(self, mock_get):
        """Тест успешной конвертации EUR → RUB: result содержит готовую сумму."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 3000.0}
        mock_get.return_value = mock_response

        transaction = {"amount": 30.0, "currency": "EUR"}
        result = convert_to_rubles(transaction)
        assert result == 3000.0

    def test_rub_currency_no_conversion(self):
        """Тест без конвертации для RUB."""
        transaction = {"amount": 1500.0, "currency": "RUB"}
        result = convert_to_rubles(transaction)
        assert result == 1500.0

    def test_unsupported_currency(self):
        """Тест для неподдерживаемой валюты."""
        transaction = {"amount": 100.0, "currency": "GBP"}
        result = convert_to_rubles(transaction)
        assert result == 0.0

    def test_missing_amount_field(self):
        """Тест отсутствия поля amount."""
        transaction = {"currency": "USD"}
        with pytest.raises(ValueError, match="Поле 'amount' отсутствует в транзакции"):
            convert_to_rubles(transaction)

    def test_missing_currency_field(self):
        """Тест отсутствия поля currency."""
        transaction = {"amount": 100.0}
        with pytest.raises(ValueError, match="Поле 'currency' отсутствует в транзакции"):
            convert_to_rubles(transaction)

    def test_invalid_amount_type(self):
        """Тест некорректного типа amount."""
        transaction = {"amount": "invalid", "currency": "USD"}
        with pytest.raises(ValueError, match="Некорректное значение 'amount'"):
            convert_to_rubles(transaction)

    @patch('external_api.requests.get')
    def test_api_request_exception(self, mock_get):
        """Тест ошибки запроса к API."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")
        transaction = {"amount": 50.0, "currency": "USD"}
        result = convert_to_rubles(transaction)
        assert result == 0.0

    @patch('external_api.requests.get')
    def test_api_response_without_result_field(self, mock_get):
        """Тест ответа API без поля result."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"RUB": 90.0}}
        mock_get.return_value = mock_response
        transaction = {"amount": 50.0, "currency": "USD"}
        result = convert_to_rubles(transaction)
        assert result == 0.0

    @patch('external_api.requests.get')
    def test_api_invalid_json_response(self, mock_get):
        """Тест невалидного JSON ответа от API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        transaction = {"amount": 50.0, "currency": "USD"}

        result = convert_to_rubles(transaction)
        assert result == 0.0

    @patch('external_api.requests.get')
    def test_api_http_error(self, mock_get):
        """Тест HTTP-ошибки от API."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        transaction = {"amount": 50.0, "currency": "USD"}
        result = convert_to_rubles(transaction)
        assert result == 0.0
