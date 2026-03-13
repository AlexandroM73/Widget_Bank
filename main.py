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