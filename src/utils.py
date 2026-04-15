import json
import os
import logging
from typing import List, Dict, Any


# Настройка логгера
def setup_logger() -> logging.Logger:
    """Настраивает логгер для модуля utils."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Устанавливаем минимальный уровень логирования

    # Создаём папку logs, если её нет
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Путь к файлу логов
    log_file_path = os.path.join(logs_dir, 'utils.log')

    # Обработчик для записи в файл (перезаписывает файл при каждом запуске)
    file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Формат записи: время, модуль, уровень, сообщение
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру (если ещё не добавлен)
    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger


# Инициализируем логгер
logger = setup_logger()


def read_json_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON‑файл с финансовыми транзакциями.

    Args:
        file_path (str): путь к JSON‑файлу.

    Returns:
        List[Dict[str, Any]]: список словарей с данными о транзакциях;
            пустой список, если файл не найден, пуст или содержит не‑список.
    """
    # Логируем попытку чтения файла
    logger.info(f"Попытка чтения JSON‑файла: {file_path}")

    # Проверяем существование файла
    if not os.path.exists(file_path):
        logger.warning(f"Файл не найден: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем, что данные — список
        if isinstance(data, list):
            logger.info(f"Успешно прочитано {len(data)} транзакций из файла {file_path}")
            return data
        else:
            logger.error(f"Данные в файле {file_path} не являются списком: {type(data)}")
            return []

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON в файле {file_path}: {e}")
        return []
    except UnicodeDecodeError as e:
        logger.error(f"Ошибка кодировки UTF-8 в файле {file_path}: {e}")
        return []
    except Exception as e:
        logger.critical(f"Непредвиденная ошибка при чтении файла {file_path}: {e}")
        return []
