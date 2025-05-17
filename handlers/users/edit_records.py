import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.admin_action import admin_actions, edit_record_month
from handlers.users.cancel import cancel
from keyboards.inline.actions import edit_records_cd, edit_record_day_keyboard, \
    all_records_day_keyboard, open_record_keyboard, check_record_comment_keyboard, check_record_delete_keyboard, \
    check_record_cancel_keyboard, back_to_day_keyboard, confirm_create_record_for_day, check_delete_day_keyboard
from loader import dp, bot
from utils.db_api.commands import get_hour_by_id, add_record_comment, \
    delete_record, cancel_record, get_user_by_id, update_day_status, add_record, delete_day


async def edit_record_days(callback: types.CallbackQuery, year, month, **kwargs):
    markup = await edit_record_day_keyboard(year=year, month=month)
    await callback.message.edit_text(text="Выберите дату", reply_markup=markup)


async def all_records_in_day(callback: types.CallbackQuery, year, month, day, **kwargs):
    markup = await all_records_day_keyboard(year=year, month=month, day=day)
    await callback.message.edit_text(text=f"Выберите запись на <b>{day}/{month}/{year}</b>", reply_markup=markup)


async def open_record(callback: types.CallbackQuery, year, month, day, hour_id, state: FSMContext, **kwargs):
    await state.update_data(hour_id=hour_id)
    record = await get_hour_by_id(hour_id=hour_id)
    markup = await open_record_keyboard(year=year, month=month, day=day, hour_id=hour_id, reserved=record.reserved)
    message_text = f"Дата: <b>{day}/{month}/{year}</b>\n" \
                   f"Время: {record.start_hour}\n\n" \
                   f"Информация по записи: \n"
    if record.user_reserved:
        user = await get_user_by_id(user_id=record.user_reserved)
        message_text += f"Клиент:\n" \
                        f"{user.first_name} {user.last_name if user.last_name else ''} {'@' + user.login if user.login else ''}\n" \
                        f"{record.description}\n"
    else:
        message_text += "<u> Открыто для записи</u>\n\n"
    message_text += f"Комментарий: {record.comment if record.comment else 'Нет комментария'}\n"
    await callback.message.edit_text(text=message_text, reply_markup=markup)


async def record_comment(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    await callback.message.edit_text(text="Напишите комментарий к записи, одним сообщением")
    await state.set_state("get_comment")


@dp.message_handler(state="get_comment")
async def get_user_comment(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        data["record_comment"] = message.text
    markup = await check_record_comment_keyboard()
    await message.answer(text="Проверьте правильность введенных данных и нажмите <b>Продолжить</b>, "
                              "если что-то не так, то нажмите <b>Ввести еще раз</b>\n\n"
                              f"{message.text}",
                         reply_markup=markup)


@dp.callback_query_handler(state="get_comment", text="confirm_record_comment")
async def add_admin_comment(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    data = await state.get_data()
    hour_id = data["hour_id"]
    comment = data["record_comment"]
    await add_record_comment(hour_id=hour_id, record_comment=comment)
    await callback.message.edit_text(text="Заметка успешно добавлена.")
    await state.finish()
    await admin_actions(message=callback, year=datetime.datetime.now().year)


@dp.callback_query_handler(state="get_comment", text="new_record_comment")
async def new_record_comment(callback: types.CallbackQuery, **kwargs):
    await callback.message.edit_text(text="Напишите комментарий к записи, одним сообщением")


async def check_record_delete(callback: types.CallbackQuery, year, month, day, hour_id, **kwargs):
    markup = await check_record_delete_keyboard(year, month, day, hour_id)
    await callback.message.edit_text(text="Удалить эту запись?", reply_markup=markup)


async def confirm_delete(callback: types.CallbackQuery, year, month, day, hour_id, state: FSMContext, **kwargs):
    record = await get_hour_by_id(hour_id=hour_id)
    await delete_record(hour_id=hour_id)
    await update_day_status(day=day, month=month, year=year)
    await callback.answer(text="Вы успешно удалили запись.", show_alert=True)
    try:
        await bot.send_message(
            text=f"Окно на <b>{record.date} {record.start_hour}</b> с вашей записью <u>УДАЛИЛ МАСТЕР</u>\n"
                 f"Если ваша запись была актуальна, пожалуйста, сделайте новую.",
            chat_id=record.user_reserved)
    except:
        pass
    await state.finish()
    await all_records_in_day(callback=callback, year=year, month=month, day=day)


async def check_record_cancel(callback: types.CallbackQuery, year, month, day, hour_id, **kwargs):
    markup = await check_record_cancel_keyboard(year, month, day, hour_id)
    await callback.message.edit_text(text="Отменить эту запись?", reply_markup=markup)


async def confirm_cancel(callback: types.CallbackQuery, hour_id, state: FSMContext, **kwargs):
    record = await get_hour_by_id(hour_id=hour_id)
    day, month, year = record.date.split("/")
    await cancel_record(hour_id=hour_id)
    await update_day_status(day=day, month=month, year=year)
    await callback.answer(text="Вы успешно отменили запись.", show_alert=True)
    await bot.send_message(text=f"Вашу запись на <b>{record.date} {record.start_hour}</b> <u>ОТМЕНИЛ МАСТЕР</u>",
                           chat_id=record.user_reserved
                           )
    await state.finish()
    await all_records_in_day(callback=callback, year=year, month=month, day=day)


async def get_record_in_day(callback: types.CallbackQuery, year, month, day, state: FSMContext, **kwargs):
    await state.update_data(date=f"{day}/{month}/{year}")
    markup = await back_to_day_keyboard(year=year, month=month, day=day)
    await callback.message.edit_text(text="Введите время первой и последней записи, <b>например 12-18</b>,\n"
                                          "Если нужно добавить 1 запись - введите время, <b>например 12</b>",
                                     reply_markup=markup)
    await state.set_state("get_hours_for_day")


@dp.callback_query_handler(state="get_hours_for_day", text="back_to_day")
async def back_to_day(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    data = await state.get_data()
    date = data["date"]
    day, month, year = date.split("/")
    await state.finish()
    await all_records_in_day(callback=callback, year=year, month=month, day=day)


@dp.message_handler(state="get_hours_for_day")
async def check_hours_for_day(message: types.Message, state: FSMContext, **kwargs):
    if len(message.text) == 2:
        hours = message.text + ":00"
    else:
        hours = message.text.split("-")
        hours = ', '.join([f"{i}:00" for i in range(int(hours[0]), int(hours[-1]) + 1, 2)])
    await state.update_data(hours=hours)
    data = await state.get_data()
    date = data["date"]
    message_text = f"Открыть запись на: {date}\n" \
                   f"Время: {hours}\n"
    markup = await confirm_create_record_for_day(date=date)
    await state.reset_state(with_data=False)
    await message.answer(text=message_text, reply_markup=markup)


async def add_hours_for_day(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    data = await state.get_data()
    date = data["date"]
    hours = data["hours"]
    for hour in hours.split(", "):
        await add_record(
            date=date,
            start_hour=hour
        )
    day, month, year = date.split("/")
    await update_day_status(day=day, month=month, year=year)
    await callback.answer(text="Выбранные записи успешно добавлены!", show_alert=True)
    await state.finish()
    await all_records_in_day(callback=callback, year=year, month=month, day=day)


async def check_delete_day(callback: types.CallbackQuery, day, month, year, **kwargs):
    markup = await check_delete_day_keyboard(day=day, month=month, year=year)
    await callback.message.edit_text(text="Удалить этот день?", reply_markup=markup)


async def confirm_delete_day(callback: types.CallbackQuery, day, month, year, **kwargs):
    await delete_day(day=day, month=month, year=year)
    await callback.answer(text="Выбранный день успешно удален!", show_alert=True)
    await edit_record_days(callback=callback, year=year, month=month)


@dp.callback_query_handler(edit_records_cd.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    current_level = callback_data.get("level")
    year = callback_data.get("year")
    month = callback_data.get("month")
    day = callback_data.get("day")
    hour_id = callback_data.get("hour_id")
    levels = {
        "1": edit_record_month,
        "2": edit_record_days,
        "3": all_records_in_day,
        "4": open_record,
        "5": record_comment,
        "6": check_record_delete,
        "7": confirm_delete,
        "8": admin_actions,
        "9": cancel,
        "10": check_record_cancel,
        "11": confirm_cancel,
        "12": get_record_in_day,
        "13": add_hours_for_day,
        "14": check_delete_day,
        "15": confirm_delete_day,
    }
    current_level_function = levels[current_level]

    await current_level_function(
        call,
        state=state,
        year=int(year),
        month=int(month),
        day=int(day),
        hour_id=int(hour_id),
    )
