from aiogram import types

from handlers.users.admin_action import admin_actions, get_history
from handlers.users.cancel import cancel
from keyboards.inline.actions import history_cd, history_days_keyboard, history_records_in_day_keyboard, history_back
from loader import dp
from utils.db_api.commands import get_user_by_id, get_history_by_id


async def history_records_days(callback: types.CallbackQuery, year, month, **kwargs):
    markup = await history_days_keyboard(year, month)
    await callback.message.edit_text(text="Выберите день", reply_markup=markup)


async def history_records_in_day(callback: types.CallbackQuery, year, month, day, **kwargs):
    markup = await history_records_in_day_keyboard(year, month, day)
    await callback.message.edit_text(text=f"Выберите запись на <b>{day}/{month}/{year}</b>", reply_markup=markup)


async def open_history_record(callback: types.CallbackQuery, year, month, day, history_id, **kwargs):
    record = await get_history_by_id(history_id)
    message_text = f"Дата: <b>{day}/{month}/{year}</b>\n" \
                   f"Время: {record.start_hour}\n\n" \
                   f"Информация по записи: \n"
    if record.user_id:
        user = await get_user_by_id(user_id=record.user_id)
        message_text += f"Клиент:\n" \
                        f"{user.first_name} {user.last_name if user.last_name else ''} {'@' + user.login if user.login else ''}\n" \
                        f"{record.description}\n"
    else:
        message_text += "<u>\nНИКТО НЕ ЗАПИСЫВАЛСЯ</u>\n\n"
    message_text += f"Комментарий: {record.comment if record.comment else 'Нет комментария'}\n"
    markup = await history_back(year, month, day)
    await callback.message.edit_text(text=message_text, reply_markup=markup)


@dp.callback_query_handler(history_cd.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get("level")
    year = callback_data.get("year")
    month = callback_data.get("month")
    day = callback_data.get("day")
    history_id = callback_data.get("history_id")
    levels = {
        "1": get_history,
        "2": history_records_days,
        "3": history_records_in_day,
        "4": open_history_record,
        "8": admin_actions,
        "9": cancel
    }
    current_level_function = levels[current_level]

    await current_level_function(
        call,
        year=int(year),
        month=int(month),
        day=int(day),
        history_id=int(history_id),
    )
