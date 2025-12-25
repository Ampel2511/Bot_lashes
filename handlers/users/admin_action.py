import datetime
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from data.config import admins
from handlers.users.cancel import cancel
from keyboards.inline.actions import actions_keyboard, choose_action_cd, create_records_keyboard, \
    edit_record_month_keyboard, get_records_variant_keyboard, get_history_month_keyboard, price_keyboard

from loader import dp
from utils.price_obj import price_lashes


@dp.message_handler(Command("admin_login"), user_id=admins)
async def admin_login(message: types.Message):
    await admin_actions(message=message, year=datetime.datetime.now().year)


async def admin_actions(message: Union[types.Message, types.CallbackQuery], year, **kwargs):
    markup = await actions_keyboard(year=year)
    if isinstance(message, types.Message):
        await message.answer(text="Выберите действие", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text("Выберите действие", reply_markup=markup)


async def list_months_admin(callback: types.CallbackQuery, year, **kwargs):
    markup = await create_records_keyboard(year=year)
    await callback.message.edit_text("Выберите месяц", reply_markup=markup)


async def get_record_variant(callback: types.CallbackQuery, year, **kwargs):
    markup = await get_records_variant_keyboard(year=year)
    await callback.message.edit_text(text="Выберите вариант", reply_markup=markup)


async def edit_record_month(callback: types.CallbackQuery, year, **kwargs):
    markup = await edit_record_month_keyboard(year=year)
    await callback.message.edit_text("Выберите месяц", reply_markup=markup)


async def get_history(callback: types.CallbackQuery, year, **kwargs):
    markup = await get_history_month_keyboard(year=year)
    await callback.message.edit_text(text="Выберите месяц", reply_markup=markup)

async def change_price(callback: types.CallbackQuery, **kwargs):
    markup = await price_keyboard()
    await callback.message.edit_text(text=f"<b>Текущий прайс:</b> \n\n"
                                          f"{price_lashes.price}",
                                     reply_markup=markup)


@dp.callback_query_handler(choose_action_cd.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    current_level = callback_data.get("level")
    year = callback_data.get("year")
    levels = {
        "1": list_months_admin,
        "2": get_record_variant,
        "3": edit_record_month,
        "4": get_history,
        "5": change_price,
        "9": cancel
    }
    current_level_function = levels[current_level]

    await current_level_function(
        call,
        state=state,
        year=int(year),
    )
