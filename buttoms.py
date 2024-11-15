from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главное меню
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📜 Список пород"), KeyboardButton(text="🐾 Введите породу")],
            [KeyboardButton(text="Факты"), KeyboardButton(text="🚀 Космос")]
        ],
        resize_keyboard=True
    )

# Подменю "Факты"
def facts_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Факт о числе"), KeyboardButton(text="Факт о дате")],
            [KeyboardButton(text="Факт о годе"), KeyboardButton(text="Случайный факт")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
