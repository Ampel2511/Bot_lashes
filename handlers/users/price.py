from aiogram import types

from data.config import price


async def lashes_price(message: types.Message):
    await message.answer(text=f"{price}")