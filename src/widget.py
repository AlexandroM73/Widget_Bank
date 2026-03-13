from datetime import datetime


def mask_account_card(input_string: str) -> str:
    """
    Обрабатывает информацию о банковских картах и счетах, возвращая строку с замаскированными данными.

    Функция определяет тип платёжного инструмента (карта или счёт) и применяет соответствующее
    правило маскировки номера.

    Args:
        input_string (str): Строка, содержащая тип и номер карты/счёта. Примеры:
            - "Visa Platinum 7000792289606361"
            - "Maestro 7000792289606361"
            - "Счёт 73654108430135874305"

    Returns:
        str: Строка с замаскированным номером в формате: "<тип> <маска>".
            Для карт: "<тип> XXXX XX** **** XXXX"
            Для счетов: "<тип> **XXXX"


    Raises:
        ValueError: Если входной номер не соответствует ожидаемому формату или длине.

    Examples:
        >>> mask_account_card("Visa Platinum 7000792289606361")
        'Visa Platinum 7000 79** **** 6361'

        >>> mask_account_card("Maestro 7000792289606361")
        'Maestro 7000 79** **** 6361'

        >>> mask_account_card("Счёт 73654108430135874305")
        'Счёт **4305'
    """
    # Убираем лишние пробелы и разбиваем строку на части
    parts = input_string.strip().split()

    if len(parts) < 2:
        raise ValueError("Входная строка должна содержать тип и номер")

    # Извлекаем номер (последние элементы строки)
    number_part = parts[-1]
    # Проверяем, что номер состоит только из цифр
    if not number_part.isdigit():
        raise ValueError("Номер должен содержать только цифры")

    # Определяем тип (всё, кроме последнего элемента)
    type_part = ' '.join(parts[:-1])

    # Обрабатываем карту (если номер 16–19 цифр)
    if 16 <= len(number_part) <= 19:
        if len(number_part) == 16:
            masked_number = f"{number_part[:4]} {number_part[4:6]}** **** {number_part[-4:]}"
        else:
            # Для карт нестандартной длины — общий шаблон
            masked_number = f"{number_part[:6]}** **** {number_part[-4:]}"
    # Обрабатываем счёт (если номер длиннее 16 цифр)
    elif len(number_part) > 16:
        masked_number = f"**{number_part[-4:]}"
    else:
        raise ValueError(f"Неподдерживаемая длина номера: {len(number_part)} цифр")

    return f"{type_part} {masked_number}"


def get_date(date_string: str) -> str:
    """
    Преобразует строку с датой из формата ISO в формат «ДД.ММ.ГГГГ».

    Функция принимает строку с датой в формате «YYYY‑MM‑DDTHH:MM:SS.ssssss»
    (например, «2024‑03‑11T02:26:18.671407») и возвращает дату в формате «ДД.ММ.ГГГГ»
    (например, «11.03.2024»).

    Args:
        date_string (str): Строка с датой и временем в формате ISO (с дробными секундами).

    Returns:
        str: Дата в формате «ДД.ММ.ГГГГ».

    Raises:
        ValueError: Если входная строка не соответствует ожидаемому формату даты.

    Examples:
        >>> get_date("2024-03-11T02:26:18.671407")
        '11.03.2024'

        >>> get_date("2023-12-25T15:30:45.123456")
        '25.12.2023'
    """
    try:
        # Парсим входную строку в объект datetime
        # Формат: %Y-%m-%dT%H:%M:%S.%f
        # %Y — год (4 цифры), %m — месяц (01–12), %d — день (01–31)
        # T — буквальный символ T
        # %H — час (00–23), %M — минуты (00–59), %S — секунды (00–59)
        # %f — микросекунды
        dt = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")

        # Форматируем дату в нужный формат (ДД.ММ.ГГГГ)
        formatted_date = dt.strftime("%d.%m.%Y")
        return formatted_date

    except ValueError as e:
        raise ValueError(
            f"Некорректный формат даты: '{date_string}'. "
            f"Ожидаемый формат: 'ГГГГ-ММ-ДДТЧЧ:ММ:СС.сссссс'. "
            f"Ошибка: {e}"
        )
