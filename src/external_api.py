import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional

# Загружаем переменные окружения из .env-файла
load_dotenv()

# Конфигурация API из переменных окружения
API_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY не найден в переменных окружения. Проверьте файл .env")
if not API_URL:
    raise ValueError("API_BASE_URL не найден в переменных окружения. Проверьте файл .env")


def get_exchange_rate(base_currency: str, target_currency: str = "RUB") -> Optional[float]:
    """
    Получает текущий курс обмена из API.

    Args:
        base_currency (str): исходная валюта (например, 'USD', 'EUR').
        target_currency (str): целевая валюта (по умолчанию 'RUB').

    Returns:
        Optional[float]: курс обмена или None при ошибке.
    """
    headers = {
        "apikey": API_KEY
    }
    params = {
        "base": base_currency,
        "symbols": target_currency
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if "rates" in data and target_currency in data["rates"]:
            return float(data["rates"][target_currency])
        else:
            print(f"Ошибка: курс для {base_currency}->{target_currency} не найден в ответе API")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None


def convert_to_rubles(transaction: Dict) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction (Dict): словарь с данными транзакции, должен содержать:
            - 'amount' (float): сумма операции;
            - 'currency' (str): валюта операции ('RUB', 'USD', 'EUR').

    Returns:
        float: сумма в рублях.
    """
    amount = float(transaction.get("amount", 0))
    currency = transaction.get("currency", "RUB").upper()

    # Если валюта уже рубли — возвращаем сумму без изменений
    if currency == "RUB":
        return amount

    # Для USD и EUR получаем курс и конвертируем
    if currency in ["USD", "EUR"]:
        rate = get_exchange_rate(currency)
        if rate is not None:
            return amount * rate
        else:
            # При ошибке API возвращаем 0.0 и выводим предупреждение
            print(f"Предупреждение: не удалось получить курс для {currency}, сумма установлена в 0.0 RUB")
            return 0.0
    else:
        # Для других валют возвращаем 0.0 с предупреждением
        print(f"Предупреждение: неподдерживаемая валюта {currency}, сумма установлена в 0.0 RUB")
        return 0.0
