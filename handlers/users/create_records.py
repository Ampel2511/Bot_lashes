from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import month_ru
from handlers.users.admin_action import admin_actions, list_months_admin
from handlers.users.cancel import cancel
from keyboards.inline.actions import create_records_cd, confirm_create_records, back_to_month_keyboard

from loader import dp
from utils.db_api.commands import add_record, add_day


async def dates_info(callback: types.CallbackQuery, year, month, state: FSMContext, **kwargs):
    await state.update_data(year=year, month=month)
    markup = await back_to_month_keyboard()
    await callback.message.edit_text(text="Введите дни на которые необходимо открыть запись \n"
                                          "<b>одним интервалом</b>: например '1-30'\n"
                                          "или \n"
                                          "<b>несколькими интервалами</b>: например '1-11, 14-25, 28-30'",
                                     reply_markup=markup)
    await state.set_state("get_days")


@dp.callback_query_handler(state="get_days", text="back_to_month")
async def back_to_month(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    data = await state.get_data()
    year = data["year"]
    await state.finish()
    await list_months_admin(callback=callback, year=year)


@dp.message_handler(state="get_days")
async def get_days(message: types.Message, state: FSMContext, **kwargs):
    days_intervals = message.text.split(", ")
    days = []
    for interval in days_intervals:
        interval = interval.split("-")
        days += [int(i) for i in range(int(interval[0]), int(interval[1]) + 1)]
    await state.update_data(days=days)
    await message.answer(text="Введите время первой и последней записи, <b>например 12-18</b>")
    await state.set_state("get_hours")


@dp.message_handler(state="get_hours")
async def get_hours(message: types.Message, state: FSMContext, **kwargs):
    hours = message.text.split("-")
    hours = ', '.join([f"{i}:00" for i in range(int(hours[0]), int(hours[-1]) + 1, 2)])
    await state.update_data(hours=hours)
    data = await state.get_data()
    year = data["year"]
    month = data["month"]
    days = data["days"]
    message_text = f"Открыть запись на: {month_ru[month]} {year}г\n"
    for day in days:
        message_text += f"{day}.{month} {hours}\n"
    markup = await confirm_create_records(year=year)
    await state.reset_state(with_data=False)
    await message.answer(text=message_text, reply_markup=markup)


async def create_records(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    data = await state.get_data()
    year = data["year"]
    month = data["month"]
    days = data["days"]
    hours = data["hours"]
    for day in days:
        for hour in hours.split(", "):
            await add_record(
                date=f"{day}/{month}/{year}",
                start_hour=hour
            )
        await add_day(
            day=day,
            month=month,
            year=year
        )
    await callback.message.edit_text(text="Выбранные записи успешно добавлены!")
    await state.finish()


@dp.callback_query_handler(create_records_cd.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    current_level = callback_data.get("level")
    year = callback_data.get("year")
    month = callback_data.get("month")
    levels = {
        "0": list_months_admin,
        "1": dates_info,
        "2": create_records,
        "8": admin_actions,
        "9": cancel,
    }
    current_level_function = levels[current_level]

    await current_level_function(
        call,
        state=state,
        year=int(year),
        month=int(month),
    )
