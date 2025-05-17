from aiogram import types
from aiogram.utils.markdown import hlink


async def about_info(message: types.Message):
    await message.answer(
        text=f"Добро пожаловать в нашу студию ресниц Ksu_Lashes. Здесь вас ждет качественное и быстрое наращивание "
             f"в комфортных условиях.\n"
             f"Мы гарантируем стойкий и долгий эффект, "
             f"а удобное расположение студии позволит без проблем приехать к нам из любой точки города."
    )
    await message.answer(
        text=f"Контакты:\n\n"
             f"📍 Адрес:\n"
             f"г. Рязань ул. Шоссейный переулок 5, Бизнес-Центр 'Аванта', 3 этаж, офис 34\n\n"
             f"{hlink('Посмотреть работы', 'https://www.instagram.com/ksu__llashes?igsh=MXl4N3JuZjVmdGRr&utm_source=qr')}\n\n"
             f"{hlink('Написать по вопросам', 'https://t.me/modinaksss')}\n",
        disable_web_page_preview=True

    )
