import logging
import os
from typing import Union


def setup_masks_logger() -> logging.Logger:
    """Настраивает отдельный логгер для модуля masks."""
    # Создаём логгер с именем модуля
    logger = logging.getLogger('masks')
    logger.setLevel(logging.DEBUG)

    # Очищаем существующие обработчики, чтобы избежать дублирования
    logger.handlers.clear()

    # Создаём папку logs в корне проекта
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Путь к файлу логов для модуля masks
    log_file_path = os.path.join(logs_dir, 'masks.log')

    # Обработчик для записи в файл с перезаписью при каждом запуске (mode='w')
    file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Формат записи: время, модуль, уровень серьёзности, сообщение
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)

    return logger


# Инициализируем отдельный логгер для модуля masks
logger = setup_masks_logger()


def get_mask_card_number(card_str: Union[int, str]) -> str:
    """Маскирует номер банковской карты по шаблону «XXXX XX** **** XXXX».

    ... (документация без изменений) ...
    """
    logger.info(f"Вызов get_mask_card_number с аргументом: {card_str} (тип: {type(card_str).__name__})")

    card_str = str(card_str)
    logger.debug(f"Преобразовано в строку: {card_str}")

    if len(card_str) != 16:
        error_msg = f"Номер карты должен содержать 16 цифр. Получено: {len(card_str)} цифр."
        logger.error(error_msg)
        raise ValueError(error_msg)

    formatted_number_card = f"{card_str[:4]} {card_str[4:6]}** **** {card_str[-4:]}"
    logger.info(f"Сформирована маска карты: {formatted_number_card}")

    return formatted_number_card


def get_mask_account(score_str: Union[int, str]) -> str:
    """Маскирует номер счёта по шаблону «**XXXX».

    ... (документация без изменений) ...
    """
    logger.info(f"Вызов get_mask_account с аргументом: {score_str} (тип: {type(score_str).__name__})")

    score_str = str(score_str)
    logger.debug(f"Преобразовано в строку: {score_str}")

    last_four = score_str[-4:]
    mask_account = f"**{last_four}"

    logger.info(f"Сформирована маска счёта: {mask_account} (исходные данные: {score_str})")
    return mask_account
