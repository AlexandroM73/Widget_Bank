import pytest
import json
from unittest.mock import patch, mock_open
from utils import read_json_transactions

# Базовые фикстуры
@pytest.fixture
def mock_file_exists():
    """Фикстура для имитации существования файла."""
    with patch("os.path.exists", return_value=True) as mock:
        yield mock

@pytest.fixture
def mock_file_not_exists():
    """Фикстура для имитации отсутствия файла."""
    with patch("os.path.exists", return_value=False) as mock:
        yield mock

# Параметризованная фикстура с расширенным набором тестовых случаев
@pytest.fixture(params=[
    # Валидный JSON-массив
    {
        "content": [
            {"id": 1, "amount": 100, "type": "income"},
            {"id": 2, "amount": -50, "type": "expense"}
        ],
        "expected": [
            {"id": 1, "amount": 100, "type": "income"},
            {"id": 2, "amount": -50, "type": "expense"}
        ],
        "description": "valid-list"
    },
    # Пустой массив
    {
        "content": [],
        "expected": [],
        "description": "empty-list"
    },
    # JSON-объект вместо массива
    {
        "content": {"total": 500},
        "expected": [],
        "description": "object-not-list"
    },
    # Повреждённый JSON
    {
        "content": "{id: 1}",
        "expected": [],
        "description": "corrupted-json"
    },
    # Пустой файл
    {
        "content": "",
        "expected": [],
        "description": "empty-file"
    },
    # Не-JSON содержимое
    {
        "content": "plain text",
        "expected": [],
        "description": "non-json-content"
    }
], ids=lambda x: x["description"])
def json_test_case(request):
    """
    Параметризованная фикстура с разными тестовыми сценариями.
    Возвращает словарь с содержимым файла и ожидаемым результатом.
    """
    return request.param

class TestReadJsonTransactions:
    def test_valid_json_file(self, mock_file_exists):
        """Тест корректного JSON‑файла с данными."""
        mock_data = [
            {"id": 1, "amount": 100, "type": "income"},
            {"id": 2, "amount": -50, "type": "expense"}
        ]
        mock_file = mock_open(read_data=json.dumps(mock_data))

        with patch("builtins.open", mock_file):
            result = read_json_transactions("dummy_path.json")

        assert result == mock_data

    def test_file_not_found(self, mock_file_not_exists):
        """Тест отсутствия файла."""
        result = read_json_transactions("nonexistent.json")
        assert result == []

    def test_empty_file(self, mock_file_exists):
        """Тест пустого файла."""
        mock_file = mock_open(read_data="")

        with patch("builtins.open", mock_file):
            result = read_json_transactions("empty.json")

        assert result == []

class TestReadJsonTransactionsParametrized:
    @pytest.mark.parametrize("exception_type", [OSError, PermissionError])
    def test_file_read_exceptions(self, exception_type, mock_file_exists):
        """
        Тест обработки исключений при чтении файла.
        Проверяет, что функция возвращает пустой список при ошибках чтения.
        """
        mock_file = mock_open()
        mock_file.side_effect = exception_type("Test exception")

        with patch("builtins.open", mock_file):
            result = read_json_transactions("problematic.json")

        assert result == []

    def test_various_json_contents(self, json_test_case, mock_file_exists):
        """
        Параметризованный тест для разных типов JSON‑содержимого.
        Запускается 6 раз с разными данными из фикстуры json_test_case.
        """
        content = json_test_case["content"]
        expected = json_test_case["expected"]

        # Если content — структура (список/словарь), преобразуем в строку
        if isinstance(content, (list, dict)):
            content_str = json.dumps(content)
        else:
            content_str = content

        mock_file = mock_open(read_data=content_str)

        with patch("builtins.open", mock_file):
            result = read_json_transactions("test.json")

        assert result == expected
