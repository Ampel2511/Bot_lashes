import datetime
from aiogram.dispatcher import FSMContext
from aiogram import types

from handlers.users.admin_action import admin_actions
from keyboards.inline.actions import price_cd, get_price_keyboard, confirm_price_keyboard, back_to_day_keyboard
from loader import dp
from utils.price_obj import price_lashes


async def lashes_price(message: types.Message):
    await message.answer(text=f"{price_lashes.price}")


async def get_new_price(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    markup = await get_price_keyboard()
    await callback.message.edit_text(text="Отправьте новый прайс: \n"
                                          "Или вернитесь в <b>Главное меню</b>", reply_markup=markup)
    await state.set_state("change_price")


@dp.callback_query_handler(state="change_price")
async def back_to_admin_with_state(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    await state.finish()
    await back_to_admin(callback=callback)


async def back_to_admin(callback: types.CallbackQuery, **kwargs):
    await admin_actions(message=callback, year=datetime.datetime.now().year)


@dp.message_handler(state="change_price")
async def confirm_price(message: types.Message, state: FSMContext, **kwargs):
    await state.update_data(new_price=message.text)
    await state.reset_state(with_data=False)
    markup = await confirm_price_keyboard()
    message_text = "Добавить новый прайс? \n\n" \
                   f"{message.text}"
    await message.answer(text=message_text, reply_markup=markup)


async def update_price(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    data = await state.get_data()
    await price_lashes(new_price=data["new_price"])
    await callback.message.edit_reply_markup()
    await state.finish()
    await admin_actions(message=callback, year=datetime.datetime.now().year)


@dp.callback_query_handler(price_cd.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    current_level = callback_data.get("level")
    levels = {
        "1": get_new_price,
        "2": update_price,
        "9": back_to_admin,
        "10": back_to_admin_with_state,
    }
    current_level_function = levels[current_level]

    await current_level_function(
        call,
        state=state,
    )
