import pytest
import os
from decorators.log_decorator import log


class TestLogDecorator:
    @pytest.fixture(autouse=True)
    def cleanup_log_files(self):
        """
        Автоматически вызываемая фикстура для очистки временных файлов
        после каждого теста.
        autouse=True — выполняется для всех тестов в классе.
        """
        yield  # Здесь выполняется тест
        # После yield — код очистки
        temp_files = [
            "test_log.txt", "another_log.txt",
            "first_log.txt", "second_log.txt"
        ]
        for log_file in temp_files:
            if os.path.exists(log_file):
                try:
                    os.remove(log_file)
                except OSError:
                    pass  # Игнорируем ошибки удаления

    def test_error_execution_console(self, capsys):
        """Тест обработки ошибки с выводом в консоль через capsys"""
        @log(force_console=True)
        def failing_function():
            raise ValueError("Тест ошибки")

        with pytest.raises(ValueError):
            failing_function()

        captured = capsys.readouterr()
        expected = "failing_function error: ValueError. Inputs: (), {}"
        assert captured.out.strip() == expected, f"Ожидалось: {expected}, получено: {captured.out.strip()}"

    def test_successful_execution_with_filename(self):
        """Тест успешного выполнения функции с записью в файл"""
        @log(filename="test_log.txt")
        def test_function(a, b):
            return a + b

        result = test_function(5, 3)
        assert result == 8

        assert os.path.exists("test_log.txt"), "Файл логов не создан"

        with open("test_log.txt", "r", encoding="utf-8") as f:
            content = f.read().strip()
        assert content == "test_function ok"

    def test_error_execution_with_filename(self):
        """Тест обработки ошибки с записью в файл"""
        @log(filename="test_log.txt")
        def failing_function(x):
            if x < 0:
                raise ValueError("Отрицательное число")
            return x * 2

        with pytest.raises(ValueError, match="Отрицательное число"):
            failing_function(-1)

        assert os.path.exists("test_log.txt"), "Файл логов не создан"

        with open("test_log.txt", "r", encoding="utf-8") as f:
            content = f.read().strip()

        expected = "failing_function error: ValueError. Inputs: (-1,), {}"
        assert content == expected

    def test_successful_execution_console(self, capsys):
        """Тест успешного выполнения с выводом в консоль"""

        @log()
        def simple_function():
            return "hello"

        result = simple_function()
        assert result == "hello"

        captured = capsys.readouterr()
        assert captured.out.strip() == "simple_function ok", f"Получено: {captured.out.strip()}"
        assert captured.err == ""

    def test_function_with_kwargs(self, capsys):
        """Тест функции с именованными аргументами"""

        @log()
        def greet(name, greeting="Привет"):
            return f"{greeting}, {name}!"

        result = greet("Анна", greeting="Здравствуйте")
        assert result == "Здравствуйте, Анна!"

        captured = capsys.readouterr()
        assert captured.out.strip() == "greet ok"

    def test_multiple_calls_same_function(self, capsys):
        """Тест многократного вызова одной функции"""

        @log()
        def multiply(a, b):
            return a * b

        multiply(2, 3)
        multiply(4, 5)

        captured = capsys.readouterr()
        lines = [line.strip() for line in captured.out.splitlines() if line.strip()]
        assert len(lines) == 2
        assert lines[0] == "multiply ok"
        assert lines[1] == "multiply ok"

    def test_different_log_files(self):
        """Тест использования разных файлов для логирования"""

        @log(filename="first_log.txt")
        def func1():
            return 1

        @log(filename="second_log.txt")
        def func2():
            raise RuntimeError("Ошибка во второй функции")

        func1()
        with pytest.raises(RuntimeError):
            func2()

        assert os.path.exists("first_log.txt"), "first_log.txt не создан"
        assert os.path.exists("second_log.txt"), "second_log.txt не создан"

        with open("first_log.txt", "r", encoding="utf-8") as f:
            assert f.read().strip() == "func1 ok"

        with open("second_log.txt", "r", encoding="utf-8") as f:
            expected = "func2 error: RuntimeError. Inputs: (), {}"
            assert f.read().strip() == expected

    def test_no_arguments_function(self, capsys):
        """Тест функции без аргументов"""

        @log()
        def get_pi():
            return 3.14159

        result = get_pi()
        assert abs(result - 3.14159) < 1e-5

        captured = capsys.readouterr()
        assert captured.out.strip() == "get_pi ok"

    def test_exception_with_args_and_kwargs(self, capsys):
        """Тест исключения с комбинацией аргументов"""

        @log()
        def complex_function(x, y, operation="add"):
            if operation == "divide" and y == 0:
                raise ZeroDivisionError("Деление на ноль")
            if operation == "add":
                return x + y
            return None

        complex_function(10, 5, operation="add")

        with pytest.raises(ZeroDivisionError):
            complex_function(10, 0, operation="divide")

        captured = capsys.readouterr()
        lines = [line.strip() for line in captured.out.splitlines() if line.strip()]

        assert len(lines) == 2
        assert lines[0] == "complex_function ok"
        expected_error = "complex_function error: ZeroDivisionError. Inputs: (10, 0), {'operation': 'divide'}"
        assert lines[1] == expected_error
