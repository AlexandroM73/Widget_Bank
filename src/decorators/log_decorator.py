import functools
from typing import Optional, Callable, TypeVar, ParamSpec

# Определяем параметры типа для корректной типизации декоратора
P = ParamSpec("P")
R = TypeVar("R")


def log(
        filename: Optional[str] = None,
        force_console: bool = False
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Декоратор для логирования выполнения функций.

    Args:
        filename: имя файла для записи логов (если None — вывод в консоль)
        force_console: принудительный вывод в консоль даже при указании filename
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            func_name = func.__name__
            try:
                result = func(*args, **kwargs)
                message = f"{func_name} ok"
                _write_log(filename, message, force_console)
                return result
            except Exception as e:
                error_type = type(e).__name__
                error_message = (
                    f"{func_name} error: {error_type}. "
                    f"Inputs: {args}, {kwargs}"
                )
                _write_log(filename, error_message, force_console)
                raise

        return wrapper

    return decorator


def _write_log(
        filename: Optional[str],
        message: str,
        force_console: bool
) -> None:
    """Вспомогательная функция для записи логов в файл или консоль"""
    if filename and not force_console:
        # Записываем в файл с кодировкой UTF-8
        try:
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        except OSError as e:
            print(f"Ошибка записи в файл {filename}: {e}")
    else:
        # Выводим в консоль
        print(message)


# === Примеры использования декоратора ===

@log(filename="mylog.txt")
def my_function(x: int, y: int) -> int:
    """Функция сложения двух чисел."""
    return x + y


@log()  # Без указания файла — логи в консоль
def failing_function(a: float, b: float) -> float:
    """Функция, которая вызывает ошибку."""
    if a == 0:
        raise ValueError("Первый аргумент не может быть нулём")
    return b / a  # Исправлено: return теперь после проверки


@log(filename="operations.log")
def multiply_numbers(a: int, b: int, c: int = 1) -> int:
    """Функция умножения трёх чисел."""
    return a * b * c


@log()
def greet(name: str, greeting: str = "Привет") -> str:
    """Функция приветствия."""
    return f"{greeting}, {name}!"


# Тестируем декоратор прямо здесь
if __name__ == "__main__":
    print("=== Запуск тестов декоратора log ===")

    # 1. Успешное выполнение с записью в файл
    print("1. Вызываем my_function(10, 5) — результат запишется в mylog.txt")
    my_function(10, 5)

    # Проверяем содержимое файла
    try:
        with open("mylog.txt", "r", encoding="utf-8") as f:
            content = f.read().strip()
        print(f"Содержимое mylog.txt: '{content}'")
    except FileNotFoundError:
        print("Файл mylog.txt не найден!")
    except Exception as e:
        print(f"Ошибка при чтении mylog.txt: {e}")

    # 2. Выполнение с ошибкой (логи в консоль)
    print("\n2. Вызываем failing_function(0, 100) — ошибка выведется в консоль")

    try:
        failing_function(0, 100)
    except ValueError as e:
        print(f"Перехвачена ошибка: {e}")  # Логируем ошибку вместо полного подавления

    # 3. Ещё один успешный вызов с записью в другой файл
    print("\n3. Вызываем multiply_numbers(2, 3, c=4) — результат в operations.log")

    multiply_numbers(2, 3, c=4)

    try:
        with open("operations.log", "r", encoding="utf-8") as f:
            content = f.read().strip()
        print(f"Содержимое operations.log: '{content}'")
    except FileNotFoundError:
        print("Файл operations.log не найден!")
    except Exception as e:
        print(f"Ошибка при чтении operations.log: {e}")

    # 4. Успешный вызов с именованными аргументами
    print("\n4. Вызываем greet('Анна', greeting='Здравствуйте') — результат в консоль")

    result = greet('Анна', greeting='Здравствуйте')
    print(f"Результат функции: '{result}'")
