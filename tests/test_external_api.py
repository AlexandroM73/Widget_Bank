from unittest.mock import patch
from external_api import convert_to_rubles


@patch('external_api.get_exchange_rate')
def test_convert_usd_to_rub(mock_get_rate):
    mock_get_rate.return_value = 90.0  # Условный курс 90 RUB/USD

    transaction = {"amount": 10.0, "currency": "USD"}
    result = convert_to_rubles(transaction)

    assert result == 900.0


def test_rub_transaction():
    transaction = {"amount": 500.0, "currency": "RUB"}
    result = convert_to_rubles(transaction)
    assert result == 500.0
