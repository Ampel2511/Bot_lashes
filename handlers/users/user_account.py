from typing import Union

from aiogram import types

from data.config import admins
from keyboards.inline.account_buttons import user_options, user_menu_cd, user_record_keyboard, \
    check_user_record_cancel_keyboard, user_history_keyboard, user_history_back_keyboard
from loader import dp, bot
from utils.db_api.commands import get_user_record, cancel_record, get_user_by_id, update_day_status, get_history_by_id


async def account_user(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await user_options()
    message_text = "Вы зашли в Личный кабинет.\n" \
                   "Здесь вы можете:\n" \
                   "1.Посмотреть вашу текущую запись\n" \
                   "2.Отменить запись\n" \
                   "3.Посмотреть историю ваших записей\n" \
                   "4.Включить\отключить уведомления\n\n" \
                   f"Чтобы узнать подробнее нажмите <b>Управление уведомлениями</b>\n\n"
    if isinstance(message, types.Message):
        await message.answer(text=message_text, reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        callback = message
        await callback.message.edit_text(text=message_text, reply_markup=markup)


@dp.callback_query_handler(text="user_record")
async def user_record(callback: types.CallbackQuery, **kwargs):
    try:
        record = await get_user_record(callback.from_user.id)
        message_text = f"<b>У вас есть активная запись.</b>\n\n" \
                       f"Запись на <b>{record.date} {record.start_hour}</b>\n" \
                       f"Контакт и заметка:\n" \
                       f"{record.description}\n"
        markup = await user_record_keyboard(hour_id=record.id)
        await callback.message.edit_text(text=message_text, reply_markup=markup)
    except:
        message_text = f'У вас сейчас нет активной записи.\n' \
                       f'Если хотите записаться, откройте меню и выберите "Записаться 📝"'
        await callback.message.edit_text(text=message_text)


async def check_cancel_user_record(callback: types.CallbackQuery, hour_id, **kwargs):
    markup = await check_user_record_cancel_keyboard(hour_id)
    await callback.message.edit_text(text="Отменить эту запись?", reply_markup=markup)


async def confirm_cancel(callback: types.CallbackQuery, hour_id, **kwargs):
    record = await get_user_record(callback.from_user.id)
    day, month, year = record.date.split("/")
    await cancel_record(hour_id=hour_id)
    await update_day_status(day=day, month=month, year=year)
    await callback.message.edit_text(text="Вы успешно отменили запись.")
    user = await get_user_by_id(callback.from_user.id)
    await bot.send_message(text=f"Клиент:\n"
                                f"{user.first_name} {user.last_name if user.last_name else ''} {'@' + user.login if user.login else ''}\n"
                                f"<u>отменил запись</u> на <b>{record.date} {record.start_hour}</b>",
                           chat_id=admins[0]
                           )


@dp.callback_query_handler(text="user_history")
async def user_history(callback: types.CallbackQuery, page: int = 1, **kwargs):
    markup = await user_history_keyboard(user_id=callback.from_user.id, page=page)
    await callback.message.edit_text(text="Выберите запись", reply_markup=markup)


async def user_history_record(callback: types.CallbackQuery, page, history_id, **kwargs):
    user_rec = await get_history_by_id(history_id=history_id)
    message_text = f"Дата: <b>{user_rec.date}</b>\n" \
                   f"Время: {user_rec.start_hour}\n\n" \
                   f"Информация по записи: \n" \
                   f"{user_rec.description}\n"
    markup = await user_history_back_keyboard(page=page)
    await callback.message.edit_text(text=message_text, reply_markup=markup)


@dp.callback_query_handler(user_menu_cd.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get("level")
    user_id = callback_data.get("user_id")
    hour_id = callback_data.get("hour_id")
    page = callback_data.get("page")
    history_id = callback_data.get("history_id")
    levels = {
        "0": account_user,
        "1": user_record,
        "2": check_cancel_user_record,
        "3": confirm_cancel,
        "4": user_history,
        "5": user_history_record
    }
    current_level_function = levels[current_level]

    await current_level_function(
        call,
        hour_id=int(hour_id),
        user_id=int(user_id),
        page=int(page),
        history_id=int(history_id),

    )
