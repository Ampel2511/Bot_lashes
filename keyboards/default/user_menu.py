from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

row1 = [
    KeyboardButton(text="Записаться 📝")
]
row2 = [
    KeyboardButton(text="Личный кабинет 💼"),
    # KeyboardButton(text="Отзывы 🗣")

]
row3 = [
    KeyboardButton(text="О нас ℹ️"),
    KeyboardButton(text="Прайс 💸")
    ]
keyboard = [
    row1,
    row2,
    row3
]

user_menu = ReplyKeyboardMarkup(keyboard=keyboard,
                                resize_keyboard=True,
                                one_time_keyboard=True
                                )
