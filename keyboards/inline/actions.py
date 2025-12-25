import calendar
import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from data.config import month_ru
from utils.db_api.commands import get_months, get_all_days, count_reserve_records, get_users_records, \
    count_history_records, get_history_records

choose_action_cd = CallbackData("action", "level", "year")
create_records_cd = CallbackData("create", "level", "year", "month")
get_records_cd = CallbackData("get", "level", "year", "month", "day")
edit_records_cd = CallbackData("edit", "level", "year", "month", "day", "hour_id")
history_cd = CallbackData("history", "level", "year", "month", "day", "history_id")
price_cd = CallbackData("price", "level")


def make_choose_action_cd(level=0, year=0):
    return choose_action_cd.new(
        level=level,
        year=year,
    )


def make_create_records_cd(level, year=0, month=0):
    return create_records_cd.new(
        level=level,
        year=year,
        month=month
    )


def make_get_records_cd(level, year=0, month=0, day=0):
    return get_records_cd.new(
        level=level,
        year=year,
        month=month,
        day=day
    )


def make_edit_records_cd(level, year=0, month=0, day=0, hour_id=0):
    return edit_records_cd.new(
        level=level,
        year=year,
        month=month,
        day=day,
        hour_id=hour_id
    )


def make_history_records_cd(level, year=0, month=0, day=0, history_id=0):
    return history_cd.new(
        level=level,
        year=year,
        month=month,
        day=day,
        history_id=history_id
    )


def make_price_cd(level):
    return price_cd.new(
        level=level
    )


async def actions_keyboard(year):
    markup = InlineKeyboardMarkup(row_width=1)

    markup.row(InlineKeyboardButton(text="Открыть запись",
                                    callback_data=make_choose_action_cd(level=1,
                                                                        year=year)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Посмотреть график",
                                    callback_data=make_choose_action_cd(level=2,
                                                                        year=year)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Редактировать запись",
                                    callback_data=make_choose_action_cd(level=3,
                                                                        year=year)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Посмотреть историю",
                                    callback_data=make_choose_action_cd(level=4,
                                                                        year=year)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Изменить прайс",
                                    callback_data=make_choose_action_cd(level=5,
                                                                        year=year)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Закрыть",
                                    callback_data=make_choose_action_cd(level=9)
                                    )
               )
    return markup


async def create_records_keyboard(year):
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup(row_width=1)
    now = datetime.datetime.now()
    if year == now.year:
        months = [_ for _ in range(now.month, 13)]
    elif year > now.year:
        months = [_ for _ in range(1, 13)]
    else:
        months = []
    for month in months:
        button_text = month_ru[month]
        callback_data = make_create_records_cd(level=CURRENT_LEVEL + 1,
                                               year=year,
                                               month=month
                                               )
        markup.insert(
            InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
        )
    pages_buttons = list()
    previous_page_text = f"⬅ {year - 1} год"
    pages_buttons.append(
        InlineKeyboardButton(
            text=previous_page_text,
            callback_data=make_create_records_cd(level=CURRENT_LEVEL,
                                                 year=year - 1
                                                 )
        )
    )

    pages_buttons.append(
        InlineKeyboardButton(
            text=f"{year} год",
            callback_data=make_create_records_cd(level=CURRENT_LEVEL,
                                                 year=year
                                                 )
        )
    )
    next_page_text = f"{year + 1} ➡"
    pages_buttons.append(
        InlineKeyboardButton(
            text=next_page_text,
            callback_data=make_create_records_cd(level=CURRENT_LEVEL,
                                                 year=year + 1
                                                 )
        )
    )

    markup.row(*pages_buttons)
    markup.row(InlineKeyboardButton(
        text="Назад",
        callback_data=make_create_records_cd(level=8,
                                             year=year)
    ))
    return markup


async def back_to_month_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)

    markup.row(InlineKeyboardButton(text="Назад", callback_data="back_to_month"))

    return markup


async def confirm_create_records(year):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Принять",
                                    callback_data=make_create_records_cd(level=2)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Ввести заново",
                                    callback_data=make_create_records_cd(
                                        level=0,
                                        year=year
                                    )
                                    )
               )
    markup.row(InlineKeyboardButton(text="Отмена",
                                    callback_data=make_create_records_cd(
                                        level=9)
                                    )
               )
    return markup


async def get_records_variant_keyboard(year):
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup(row_width=1)

    markup.row(InlineKeyboardButton(
        text="Выбрать месяц",
        callback_data=make_get_records_cd(level=CURRENT_LEVEL + 1,
                                          year=year)
    ))
    markup.row(InlineKeyboardButton(
        text="Записи на сегодня",
        callback_data=make_get_records_cd(level=4)
    ))
    markup.row(InlineKeyboardButton(
        text="Назад",
        callback_data=make_get_records_cd(level=8,
                                          year=year)
    ))
    return markup


async def get_records_month_keyboard(year):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=1)

    months = await get_months(year=year)
    for month in months:
        button_text = month_ru[month]
        callback_data = make_get_records_cd(level=CURRENT_LEVEL + 1,
                                            year=year,
                                            month=month
                                            )
        markup.insert(
            InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
        )
    pages_buttons = list()
    previous_page_text = f"⬅ {year - 1} год"
    pages_buttons.append(
        InlineKeyboardButton(
            text=previous_page_text,
            callback_data=make_get_records_cd(level=CURRENT_LEVEL,
                                              year=year - 1
                                              )
        )
    )

    pages_buttons.append(
        InlineKeyboardButton(
            text=f"{year} год",
            callback_data=make_get_records_cd(level=CURRENT_LEVEL,
                                              year=year
                                              )
        )
    )
    next_page_text = f"{year + 1} ➡"
    pages_buttons.append(
        InlineKeyboardButton(
            text=next_page_text,
            callback_data=make_get_records_cd(level=CURRENT_LEVEL,
                                              year=year + 1
                                              )
        )
    )

    markup.row(*pages_buttons)
    markup.row(InlineKeyboardButton(
        text="Назад",
        callback_data=make_get_records_cd(level=CURRENT_LEVEL - 1,
                                          year=year)
    ))
    return markup


async def get_records_days_keyboard(year, month):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=3)
    days = await get_all_days(year=year, month=month)

    for day in days:
        records_number = await count_reserve_records(year=year, month=month, day=day)
        button_text = f"{day}.{month} - {f'({records_number}) ✅' if records_number > 0 else f'({records_number}) ❌'}"
        callback_data = make_get_records_cd(level=CURRENT_LEVEL + 1,
                                            year=year,
                                            month=month,
                                            day=day
                                            )
        markup.insert(
            InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
        )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_get_records_cd(level=CURRENT_LEVEL - 1,
                                                                      year=year
                                                                      )
                                    )
               )
    return markup


async def edit_record_month_keyboard(year):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=1)

    months = await get_months(year=year)
    for month in months:
        button_text = month_ru[month]
        callback_data = make_edit_records_cd(level=CURRENT_LEVEL + 1,
                                             year=year,
                                             month=month
                                             )
        markup.insert(
            InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
        )
    pages_buttons = list()
    previous_page_text = f"⬅ {year - 1} год"
    pages_buttons.append(
        InlineKeyboardButton(
            text=previous_page_text,
            callback_data=make_edit_records_cd(level=CURRENT_LEVEL,
                                               year=year - 1
                                               )
        )
    )

    pages_buttons.append(
        InlineKeyboardButton(
            text=f"{year} год",
            callback_data=make_edit_records_cd(level=CURRENT_LEVEL,
                                               year=year
                                               )
        )
    )
    next_page_text = f"{year + 1} ➡"
    pages_buttons.append(
        InlineKeyboardButton(
            text=next_page_text,
            callback_data=make_edit_records_cd(level=CURRENT_LEVEL,
                                               year=year + 1
                                               )
        )
    )

    markup.row(*pages_buttons)
    markup.row(InlineKeyboardButton(
        text="Назад",
        callback_data=make_edit_records_cd(level=8,
                                           year=year)
    ))
    return markup


async def edit_record_day_keyboard(year, month):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=3)
    days = await get_all_days(year=year, month=month)

    for day in days:
        records_number = await count_reserve_records(year=year, month=month, day=day)
        button_text = f"{day}.{month} - {f'({records_number}) ✅' if records_number > 0 else f'({records_number}) ❌'}"
        callback_data = make_edit_records_cd(level=CURRENT_LEVEL + 1,
                                             year=year,
                                             month=month,
                                             day=day
                                             )
        markup.insert(
            InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
        )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_edit_records_cd(level=CURRENT_LEVEL - 1,
                                                                       year=year
                                                                       )
                                    )
               )
    return markup


async def all_records_day_keyboard(year, month, day):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup(row_width=1)
    records = await get_users_records(year=year, month=month, day=day)

    if len(records) == 0:
        markup.insert(
            InlineKeyboardMarkup(text="Добавить запись", callback_data=make_edit_records_cd(level=12,
                                                                                            year=year,
                                                                                            month=month,
                                                                                            day=day)
                                 )
        )
        markup.insert(
            InlineKeyboardMarkup(text="Удалить день", callback_data=make_edit_records_cd(level=14,
                                                                                         year=year,
                                                                                         month=month,
                                                                                         day=day)
                                 )
        )
    else:
        for record in records:
            button_text = f"{record.start_hour}{' - Забронировано' if record.reserved else ''}"
            callback_data = make_edit_records_cd(level=CURRENT_LEVEL + 1,
                                                 hour_id=record.id,
                                                 year=year,
                                                 month=month,
                                                 day=day
                                                 )
            markup.insert(
                InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
            )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_edit_records_cd(level=CURRENT_LEVEL - 1,
                                                                       year=year,
                                                                       month=month,
                                                                       )
                                    )
               )
    return markup


async def back_to_day_keyboard(year, month, day):
    markup = InlineKeyboardMarkup(row_width=1)

    markup.row(InlineKeyboardButton(text="Назад", callback_data="back_to_day"))

    return markup


async def confirm_create_record_for_day(date):
    markup = InlineKeyboardMarkup(row_width=1)
    day, month, year = date.split("/")
    markup.row(InlineKeyboardButton(text="Принять",
                                    callback_data=make_edit_records_cd(level=13)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Ввести заново",
                                    callback_data=make_edit_records_cd(
                                        level=12,
                                        year=year,
                                        month=month,
                                        day=day
                                    )
                                    )
               )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_edit_records_cd(level=3,
                                                                       year=year,
                                                                       month=month,
                                                                       day=day,
                                                                       )
                                    )
               )
    return markup


async def check_delete_day_keyboard(year, month, day):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Продолжить",
                                    callback_data=make_edit_records_cd(level=15,
                                                                       year=year,
                                                                       month=month,
                                                                       day=day)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_edit_records_cd(level=3,
                                                                       year=year,
                                                                       month=month,
                                                                       day=day,
                                                                       )
                                    )
               )
    return markup


async def open_record_keyboard(year, month, day, hour_id, reserved):
    CURRENT_LEVEL = 4
    markup = InlineKeyboardMarkup(row_width=1)
    if reserved:
        markup.row(InlineKeyboardButton(
            text="Добавить комментарий",
            callback_data=make_edit_records_cd(level=5,
                                               hour_id=hour_id)
        ))
        markup.row(InlineKeyboardButton(
            text="Отменить запись",
            callback_data=make_edit_records_cd(level=10,
                                               hour_id=hour_id,
                                               year=year,
                                               month=month,
                                               day=day)
        ))
    markup.row(InlineKeyboardButton(
        text="Удалить запись",
        callback_data=make_edit_records_cd(level=6,
                                           hour_id=hour_id,
                                           year=year,
                                           month=month,
                                           day=day)
    ))
    markup.row(InlineKeyboardButton(
        text="Назад",
        callback_data=make_edit_records_cd(level=CURRENT_LEVEL - 1,
                                           year=year,
                                           month=month,
                                           day=day)
    ))
    return markup


async def check_record_comment_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Продолжить",
                                    callback_data="confirm_record_comment"
                                    )
               )
    markup.row(InlineKeyboardButton(text="Ввести еще раз",
                                    callback_data="new_record_comment"
                                    )
               )
    return markup


async def check_record_delete_keyboard(year, month, day, hour_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Продолжить",
                                    callback_data=make_edit_records_cd(level=7,
                                                                       hour_id=hour_id,
                                                                       year=year,
                                                                       month=month,
                                                                       day=day)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_edit_records_cd(level=4,
                                                                       year=year,
                                                                       month=month,
                                                                       day=day
                                                                       )
                                    )
               )
    return markup


async def check_record_cancel_keyboard(year, month, day, hour_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Продолжить",
                                    callback_data=make_edit_records_cd(level=11,
                                                                       hour_id=hour_id)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_edit_records_cd(level=4,
                                                                       year=year,
                                                                       month=month,
                                                                       day=day
                                                                       )
                                    )
               )
    return markup


async def get_history_month_keyboard(year):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=1)

    for month, month_name in month_ru.items():
        button_text = month_name
        callback_data = make_history_records_cd(level=CURRENT_LEVEL + 1,
                                                year=year,
                                                month=month
                                                )
        markup.insert(
            InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
        )
    pages_buttons = list()
    previous_page_text = f"⬅ {year - 1} год"
    pages_buttons.append(
        InlineKeyboardButton(
            text=previous_page_text,
            callback_data=make_history_records_cd(level=CURRENT_LEVEL,
                                                  year=year - 1
                                                  )
        )
    )

    pages_buttons.append(
        InlineKeyboardButton(
            text=f"{year} год",
            callback_data=make_history_records_cd(level=CURRENT_LEVEL,
                                                  year=year
                                                  )
        )
    )
    next_page_text = f"{year + 1} ➡"
    pages_buttons.append(
        InlineKeyboardButton(
            text=next_page_text,
            callback_data=make_history_records_cd(level=CURRENT_LEVEL,
                                                  year=year + 1
                                                  )
        )
    )

    markup.row(*pages_buttons)
    markup.row(InlineKeyboardButton(
        text="Назад",
        callback_data=make_history_records_cd(level=8,
                                              year=year)
    ))
    return markup


async def history_days_keyboard(year, month):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=3)

    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        records_number = await count_history_records(year=year, month=month, day=day)
        button_text = f"{day}.{month} - {f'({records_number}) ✅' if records_number > 0 else f'({records_number}) ❌'}"
        callback_data = make_history_records_cd(level=CURRENT_LEVEL + 1,
                                                year=year,
                                                month=month,
                                                day=day
                                                )
        markup.insert(
            InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
        )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_history_records_cd(level=CURRENT_LEVEL - 1,
                                                                          year=year
                                                                          )
                                    )
               )
    return markup


async def history_records_in_day_keyboard(year, month, day):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup(row_width=1)
    records = await get_history_records(year=year, month=month, day=day)
    for record in records:
        button_text = f"{record.start_hour}{' ✅' if record.user_id else ' ❌'}"
        callback_data = make_history_records_cd(level=CURRENT_LEVEL + 1,
                                                history_id=record.id,
                                                year=year,
                                                month=month,
                                                day=day
                                                )
        markup.insert(InlineKeyboardMarkup(text=button_text, callback_data=callback_data))
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_history_records_cd(level=CURRENT_LEVEL - 1,
                                                                          year=year,
                                                                          month=month,
                                                                          )
                                    )
               )
    return markup


async def history_back(year, month, day):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_history_records_cd(level=3,
                                                                          year=year,
                                                                          month=month,
                                                                          day=day,
                                                                          )
                                    )
               )
    return markup


async def price_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Изменить прайс",
                                    callback_data=make_price_cd(level=1)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_price_cd(level=9)
                                    )
               )
    return markup


async def get_price_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Главное меню",
                                    callback_data=make_price_cd(level=10)
                                    )
               )
    return markup

async def confirm_price_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Принять",
                                    callback_data=make_price_cd(level=2)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Ввести заново",
                                    callback_data=make_price_cd(level=1)
                                    )
               )
    return markup
