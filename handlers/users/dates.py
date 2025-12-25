import datetime
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton

from data.config import admins
from handlers.users.cancel import cancel
from keyboards.inline.get_days import dates_markup, months_markup, date_cd, hours_markup, continue_user_contact_markup, \
    check_user_contact_markup, choose_user_comment_markup, check_user_comment_markup, check_user_record_markup
from loader import dp, bot
from utils.db_api.commands import get_hour_by_id, update_record, add_user, get_user_by_id, get_user_record, get_months


async def list_months(message: Union[types.Message, types.CallbackQuery], year, **kwargs):
    markup = await months_markup(year=year)

    if isinstance(message, types.Message):
        try:
            user_records = await get_user_record(user_id=message.from_user.id)
            if len(user_records) == 2:
                for record in user_records:
                    message_text = f"<b>У вас есть активная запись.</b>\n\n" \
                                   f"Запись на <b>{record.date} {record.start_hour}</b>\n" \
                                   f"Контакт и заметка:\n" \
                                   f"{record.description}\n\n" \
                                   f"Отменить запись можно через\n" \
                                   f"<b>Личный кабинет 💼</b> --> <b>Активная запись</b>\n"
                    await message.answer(text=message_text)
            else:
                record = user_records[0]
                message_text = f"<b>У вас есть активная запись.</b>\n\n" \
                               f"Запись на <b>{record.date} {record.start_hour}</b>\n" \
                               f"Контакт и заметка:\n" \
                               f"{record.description}\n"
                if len(await get_months(year=year)) == 2:
                    message_text += f"\nВы можете записаться на <b>другой</b> доступный месяц."
                    await message.answer(text=message_text)
                    await message.answer("Выберите месяц", reply_markup=markup)
                else:
                    await message.answer(text=message_text)
        except:
            await message.answer("Выберите месяц", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text("Выберите месяц", reply_markup=markup)


async def list_dates(callback: types.CallbackQuery, year, month, **kwargs):
    markup = await dates_markup(day=datetime.datetime.now().day, year=year, month=month)
    await callback.message.edit_text(text="Выберите дату", reply_markup=markup)


async def list_hours(callback: types.CallbackQuery, year, month, day, **kwargs):
    markup = await hours_markup(year=year, month=month, day=day)
    await callback.message.edit_text(text="Выберите время", reply_markup=markup)


async def info_continue(callback: types.CallbackQuery, year, month, day, hour_id, state: FSMContext, **kwargs):
    await state.update_data(hour_id=hour_id)
    try:
        data = await state.get_data()
        user_description = data["user_description"]
        await check_user_record(callback=callback, state=state)
    except:
        await callback.message.delete()
        await callback.message.answer(text="‼️ Важная информация: ‼️\n\n"
                                           "Для новых клиентов предоплата 500₽\n\n"
                                           "<b>Предоплата не возвращается в случае:</b>\n"
                                           "1️⃣ Отмена записи меньше чем за 2е суток\n"
                                           "2️⃣ Опоздание более чем на 15 минут\n\n"
                                           "<b>Для всех клиентов:</b>\n"
                                           "При опоздании более чем на 15 минут - запись отменяется\n\n"
                                           "Оплата производится:\n"
                                           f"1️⃣ СБП на Т-Банк по номеру +79537349669, после оплаты необходимо прислать чек перевода в ЛС\n"
                                           "2️⃣ Наличными")
        markup = await continue_user_contact_markup(year=year, month=month, day=day)
        await callback.message.answer(
            text="Вам необходимо указать ваши контактные данные, по которым с вами можно связаться."
                 "Нажмите <b>Продолжить</b>, чтобы перейти к вводу контактных данных или "
                 "<b>Назад</b>, чтобы вернуться к выбору времени.",
            reply_markup=markup)


async def get_user_contact(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    await state.set_state("get_user_contact")
    await callback.message.edit_text(text="Отправьте ваши контактные данные")


@dp.message_handler(state="get_user_contact")
async def check_user_contact(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        try:
            data["user_description"]["user_contact"] = message.text
        except:
            await state.update_data(user_description=dict(user_contact=message.text,
                                                          user_comment=None)
                                    )
    markup = await check_user_contact_markup()
    await message.answer(text="Проверьте правильность введенных данных и нажмите <b>Продолжить</b>, "
                              "если что-то не так, то нажмите <b>Ввести еще раз</b>\n\n"
                              f"{message.text}",
                         reply_markup=markup)


@dp.callback_query_handler(text="new_contact", state="get_user_contact")
async def new_user_contact(callback: types.CallbackQuery, **kwargs):
    await callback.message.edit_text(text="Отправьте ваши контактные данные")


@dp.callback_query_handler(text="confirm_contact", state="get_user_contact")
async def confirm_user_contact(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    markup = await choose_user_comment_markup()
    await callback.message.edit_text(
        text="Если вам необходимо что-то добавить к записи для мастера, "
             "комментарий или пожелание, нажмите <b>Добавить заметку</b>, "
             "если в этом нет необходимости, нажмите <b>Продолжить</b>",
        reply_markup=markup
    )
    await state.reset_state(with_data=False)


@dp.callback_query_handler(text="get_user_comment")
async def get_user_comment(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    await callback.message.edit_text(text="Напишите одним сообщением, "
                                       "что хотите добавить в заметку к вашей записи для мастера:")
    await state.set_state("add_comment")


@dp.message_handler(state="add_comment")
async def add_comment(message: types.Message, state: FSMContext, **kwargs):
    async with state.proxy() as data:
        data["user_description"]["user_comment"] = message.text
    markup = await check_user_comment_markup()
    await message.answer(text="Проверьте правильность введенных данных и нажмите <b>Продолжить</b>, "
                              "если что-то не так, то нажмите <b>Ввести еще раз</b>\n\n"
                              f"{message.text}",
                         reply_markup=markup)


@dp.callback_query_handler(text="new_comment", state="add_comment")
async def new_user_comment(callback: types.CallbackQuery, **kwargs):
    await callback.message.edit_text(text="Напишите одним сообщением, "
                                          "что хотите добавить в заметку к вашей записи для мастера:")


@dp.callback_query_handler(text="check_user_record", state="add_comment")
async def confirm_user_comment(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    await state.reset_state(with_data=False)
    await check_user_record(callback=callback, state=state)


@dp.callback_query_handler(text="check_user_record")
async def check_user_record(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    data = await state.get_data()
    hour_id = int(data["hour_id"])
    user_contact = data["user_description"]["user_contact"]
    user_comment = data["user_description"]["user_comment"]
    open_hour = await get_hour_by_id(hour_id=hour_id)
    markup = await check_user_record_markup(year=open_hour.date[-4:])
    if user_comment:
        markup.row(InlineKeyboardButton(text="Изменить заметку",
                                        callback_data="get_user_comment")
                   )
    await callback.message.edit_text(text=f"Проверьте правильность информации о вашей записи: \n\n"
                                          f"<u>Запись на</u> <b>{open_hour.date} - {open_hour.start_hour}</b>\n\n"
                                          f"<b>Контакт </b> {user_contact}\n\n"
                                          f"{'<b>Заметка:</b> ' + user_comment if user_comment else ''}",
                                     reply_markup=markup)
    await state.reset_state(with_data=False)


@dp.callback_query_handler(text="create_record")
async def create_record(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    data = await state.get_data()
    hour_id = int(data["hour_id"])
    user_contact = data["user_description"]["user_contact"]
    user_comment = data["user_description"]["user_comment"]
    hour_obj = await get_hour_by_id(hour_id=hour_id)
    if hour_obj.reserved:
        await callback.message.edit_text(text="Данное время уже занято. Пожалуйста, выберите другое.")
        day, month, year = hour_obj.date.split("/")
        markup = await hours_markup(year=year, month=month, day=day)
        await callback.message.answer(text="Выберите время", reply_markup=markup)
    else:
        try:
            user = await get_user_by_id(user_id=callback.from_user.id)
            try:
                user_record = [_ for _ in await get_user_record(user_id=user.user_id)][0]
                if hour_obj.date.split("/")[1] == user_record.date.split("/")[1]:
                    message_text = f"<b>У вас есть активная запись.</b>\n\n" \
                                   f"Запись на <b>{user_record.date} {user_record.start_hour}</b>\n" \
                                   f"Контакт и заметка:\n" \
                                   f"{user_record.description}\n\n" \
                                   f"Вы можете записаться на <b>другой</b> доступный месяц."
                    await callback.message.edit_text(text=message_text)
                    await state.finish()
                    markup = await months_markup(year=int(hour_obj.date.split("/")[2]))
                    await callback.message.answer("Выберите месяц", reply_markup=markup)
                    return
                else:
                    await update_record(hour_id=hour_id, user_reserved=user.user_id,
                                        description=f"{user_contact}\n"
                                                    f"{user_comment if user_comment else ''}", )
            except:
                await update_record(hour_id=hour_id, user_reserved=user.user_id,
                                    description=f"{user_contact}\n"
                                                f"{user_comment if user_comment else ''}", )
        except:
            await add_user(
                user_id=callback.from_user.id,
                first_name=callback.from_user.first_name,
                last_name=callback.from_user.last_name,
                login=callback.from_user.username,
                contact=user_contact,
                comment=None,
            )
            await update_record(hour_id=hour_id, user_reserved=callback.from_user.id,
                                description=f"{user_contact}\n"
                                            f"{user_comment if user_comment else ''}", )
        open_hour = await get_hour_by_id(hour_id=hour_id)
        user = await get_user_by_id(user_id=callback.from_user.id)
        await bot.send_message(text=f"<b>НОВАЯ ЗАПИСЬ!</b> \n\n"
                                    f"<u>Запись на</u> <b>{open_hour.date} - {open_hour.start_hour}</b>\n\n"
                                    f"Клиент:\n"
                                    f"{user.first_name} {user.last_name if user.last_name else ''} {'@' + user.login if user.login else ''}\n"
                                    f"<b>Описание:</b>\n"
                                    f"{open_hour.description}",
                               chat_id=admins[0]
                               )
        await callback.message.edit_text(
            text=f"Вы успешно записались на <b>{open_hour.date} - {open_hour.start_hour}</b>")
        await state.finish()



@dp.callback_query_handler(date_cd.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    current_level = callback_data.get("level")
    year = callback_data.get("year")
    month = callback_data.get("month")
    day = callback_data.get("day")
    hour_id = callback_data.get("hour_id")
    levels = {
        "0": list_months,
        "1": list_dates,
        "2": list_hours,
        "3": info_continue,
        "4": get_user_contact,
        "9": cancel
    }
    current_level_function = levels[current_level]

    await current_level_function(
        call,
        state=state,
        year=int(year),
        month=int(month),
        day=int(day),
        hour_id=int(hour_id)
    )
