import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.admin_action import admin_actions, get_record_variant
from handlers.users.cancel import cancel
from keyboards.inline.actions import actions_keyboard, get_records_month_keyboard, get_records_days_keyboard, \
    get_records_cd

from loader import dp
from utils.db_api.commands import get_users_records, get_user_by_id


async def get_records_month(callback: types.CallbackQuery, year, **kwargs):
    markup = await get_records_month_keyboard(year=year)
    await callback.message.edit_text("Выберите месяц", reply_markup=markup)


async def get_records_days(callback: types.CallbackQuery, year, month, **kwargs):
    markup = await get_records_days_keyboard(year=year, month=month)
    await callback.message.edit_text(text="Выберите дату, в скобках указано сколько записей имеется на этот день",
                                     reply_markup=markup)


async def print_records(callback: types.CallbackQuery, year, month, day, **kwargs):
    records = await get_users_records(year=year, month=month, day=day)
    await callback.message.edit_text(text=f"<b>Записи на {day}/{month}/{year}</b>")
    for record in records:
        message_text = f"<u>Время: {record.start_hour}\n\n</u>"
        if record.reserved:
            user = await get_user_by_id(user_id=record.user_reserved)
            message_text += f"Клиент:\n" \
                            f"{user.first_name} {user.last_name if user.last_name else ''} {'@' + user.login if user.login else ''}\n\n" \
                            f"Информация по записи: \n" \
                            f"{record.description}\n\n"
        else:
            message_text += f"<b>Открыто для записи</b>\n\n"
        message_text += f"Комментарий: {record.comment if record.comment else 'Нет комментария'}"
        await callback.message.answer(text=message_text)
    markup = await actions_keyboard(year=year)
    await callback.message.answer("Выберите действие", reply_markup=markup)


async def get_today_records(callback: types.CallbackQuery, **kwargs):
    now = datetime.datetime.now()
    await print_records(callback, year=now.year, month=now.month, day=now.day)


@dp.callback_query_handler(get_records_cd.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    current_level = callback_data.get("level")
    year = callback_data.get("year")
    month = callback_data.get("month")
    day = callback_data.get("day")
    levels = {
        "0": get_record_variant,
        "1": get_records_month,
        "2": get_records_days,
        "3": print_records,
        "4": get_today_records,
        "8": admin_actions,
        "9": cancel,
    }
    current_level_function = levels[current_level]

    await current_level_function(
        call,
        state=state,
        year=int(year),
        month=int(month),
        day=int(day),
    )
