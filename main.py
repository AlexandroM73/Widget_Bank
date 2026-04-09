from src.masks import get_mask_account, get_mask_card_number
from src.widget import mask_account_card, get_date

# Используем функции
card = "7000792289606361"
account = "73654108430135874305"

print(get_mask_card_number(card))  # 7000 79** **** 6361
print(get_mask_account(account))  # **4305
print(get_date("2024-03-11T02:26:18.671407"))
print(mask_account_card("Visa Platinum 7000792289606361"))
print(mask_account_card("Счёт 73654108430135874305"))

def main():
    """Основная функция для взаимодействия с пользователем."""
    # Пример данных (в реальном проекте — загрузка из файла/БД)
    transactions = [
        {'id': 1, 'description': 'Покупка в магазине Пятерочка'},
        {'id': 2, 'description': 'Оплата услуг интернета'},
        {'id': 3, 'description': 'Перевод другу'},
        {'id': 4, 'description': 'Оплата мобильной связи'}
    ]

    print("Добро пожаловать в систему анализа транзакций!")
    print("Доступные команды:")
    print("1 — Поиск транзакций по описанию")
    print("2 — Подсчёт транзакций по категориям")
    print("0 — Выход")

    while True:
        choice = input("\nВыберите команду: ").strip()

        if choice == '1':
            search_term = input("Введите строку для поиска: ")
            results = search_transactions_by_description(transactions, search_term)
            print(f"Найдено транзакций: {len(results)}")
            for transaction in results:
                print(f"- ID: {transaction['id']}, Описание: {transaction['description']}")

        elif choice == '2':
            print("Доступные категории: магазин, интернет, перевод, связь")
            categories_input = input("Введите категории через запятую: ")
            categories = [cat.strip() for cat in categories_input.split(',')]
            counts = count_transactions_by_categories(transactions, categories)
            print("Результаты подсчёта:")
            for category, count in counts.items():
                print(f"- {category}: {count} транзакций")

        elif choice == '0':
            print("До свидания!")
            break

        else:
            print("Неверная команда. Попробуйте снова.")
