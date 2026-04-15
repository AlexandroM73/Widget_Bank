import requests
import os
import logging
from dotenv import load_dotenv
from typing import Dict

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env-файла
load_dotenv()

# Конфигурация API из переменных окружения
API_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY не найден в переменных окружения. Проверьте файл .env")
if not API_URL:
    raise ValueError("API_BASE_URL не найден в переменных окружения. Проверьте файл .env")

# Поддерживаемые валюты
SUPPORTED_CURRENCIES = {"USD", "EUR"}


def convert_to_rubles(transaction: Dict) -> float:
    """
    Конвертирует сумму транзакции в рубли, используя поле 'result' из ответа API.
    'result' содержит уже готовую сумму в рублях.

    Args:
        transaction (Dict): словарь с данными транзакции, должен содержать:
            - 'amount' (float): сумма операции;
            - 'currency' (str): валюта операции ('RUB', 'USD', 'EUR').

    Returns:
        float: сумма в рублях (готовый результат из 'result' или 0.0 при ошибках).

    Raises:
        ValueError: если отсутствуют обязательные поля в транзакции или некорректные данные.
    """
    # Извлекаем данные из транзакции
    amount = transaction.get("amount")
    currency = transaction.get("currency")

    # Валидация входных данных
    if amount is None:
        raise ValueError("Поле 'amount' отсутствует в транзакции")
    if currency is None:
        raise ValueError("Поле 'currency' отсутствует в транзакции")

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        raise ValueError(f"Некорректное значение 'amount': {amount}")

    currency = currency.upper()
    logger.debug(f"Обрабатываем транзакцию: {amount} {currency}")

    # Если валюта уже рубли — возвращаем сумму без изменений
    if currency == "RUB":
        logger.debug("Валюта — RUB, конвертация не требуется")
        return amount

    # Проверка поддерживаемых валют
    if currency not in SUPPORTED_CURRENCIES:
        logger.warning(f"Неподдерживаемая валюта {currency}, возвращаем 0.0 RUB")
        return 0.0

    # Параметры запроса к API
    headers = {"apikey": API_KEY}
    params = {"base": currency, "symbols": "RUB"}

    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()  # Инициализация внутри try
        logger.debug(f"Ответ API: {data}")

        if "result" in data:
            converted_amount = data["result"]
            logger.info(f"Конвертировано: {amount} {currency} → {converted_amount:.2f} RUB")
            return float(converted_amount)
        else:
            logger.error(f"Поле 'result' отсутствует в ответе API для {currency}: {data}")
            return 0.0

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        return 0.0
    except (KeyError, TypeError, ValueError) as e:
        # data теперь гарантированно определена или None
        logger.error(f"Ошибка обработки ответа API: {e}, данные: {data if 'data' in locals() else 'N/A'}")
        return 0.0
