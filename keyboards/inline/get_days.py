from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from data.config import month_ru
from utils.db_api.commands import get_months, get_free_days, get_hours

date_cd = CallbackData("date", "level", "year", "month", "day", "hour_id")


def make_date_cd(level, year=0, month=0, day=0, hour_id=0):
    return date_cd.new(
        level=level,
        year=year,
        month=month,
        day=day,
        hour_id=hour_id,
    )


async def months_markup(year):
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup(row_width=1)

    months = await get_months(year=year)
    for month in months:
        button_text = month_ru[month]
        callback_data = make_date_cd(level=CURRENT_LEVEL + 1,
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
            callback_data=make_date_cd(level=CURRENT_LEVEL,
                                       year=year - 1
                                       )
        )
    )

    pages_buttons.append(
        InlineKeyboardButton(
            text=f"{year} год",
            callback_data=make_date_cd(level=CURRENT_LEVEL,
                                       year=year
                                       )
        )
    )
    next_page_text = f"{year + 1} ➡"
    pages_buttons.append(
        InlineKeyboardButton(
            text=next_page_text,
            callback_data=make_date_cd(level=CURRENT_LEVEL,
                                       year=year + 1
                                       )
        )
    )

    markup.row(*pages_buttons)
    markup.row(InlineKeyboardButton(
        text="Закрыть",
        callback_data=make_date_cd(level=9)
    ))
    return markup


async def dates_markup(day, month, year):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=3)

    days = await get_free_days(day=day, month=month, year=year)

    for day in days:
        button_text = f"{day}.{month}"
        callback_data = make_date_cd(level=CURRENT_LEVEL + 1,
                                     year=year,
                                     month=month,
                                     day=day
                                     )
        markup.insert(
            InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
        )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_date_cd(level=CURRENT_LEVEL - 1,
                                                               year=year
                                                               )
                                    )
               )
    return markup


async def hours_markup(year, month, day):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=1)

    hours = await get_hours(year=year, month=month, day=day)

    for obj in hours:
        button_text = obj.start_hour
        callback_data = make_date_cd(level=CURRENT_LEVEL + 1,
                                     year=year,
                                     month=month,
                                     day=day,
                                     hour_id=obj.id
                                     )
        markup.insert(
            InlineKeyboardMarkup(text=button_text, callback_data=callback_data)
        )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_date_cd(level=CURRENT_LEVEL - 1,
                                                               year=year,
                                                               month=month
                                                               )
                                    )
               )
    return markup


async def continue_user_contact_markup(year, month, day):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Продолжить",
                                    callback_data=make_date_cd(level=CURRENT_LEVEL + 1
                                                               )
                                    )
               )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_date_cd(level=CURRENT_LEVEL - 1,
                                                               year=year,
                                                               month=month,
                                                               day=day
                                                               )
                                    )
               )
    return markup


async def check_user_contact_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Продолжить",
                                    callback_data="confirm_contact"
                                    )
               )
    markup.row(InlineKeyboardButton(text="Ввести еще раз",
                                    callback_data="new_contact"
                                    )
               )
    return markup


async def choose_user_comment_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Добавить заметку",
                                    callback_data="get_user_comment"
                                    )
               )
    markup.row(InlineKeyboardButton(text="Продолжить",
                                    callback_data="check_user_record"
                                    )
               )
    return markup


async def check_user_comment_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Продолжить",
                                    callback_data="check_user_record"
                                    )
               )
    markup.row(InlineKeyboardButton(text="Ввести еще раз",
                                    callback_data="new_comment"
                                    )
               )
    return markup

async def check_user_record_markup(year):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Изменить контакт",
                                    callback_data=make_date_cd(level=4)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Изменить время",
                                    callback_data=make_date_cd(level=0,
                                                               year=year)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Записаться",
                                    callback_data="create_record"
                                    )
               )
    markup.row(InlineKeyboardButton(text="Отмена",
                                    callback_data=make_date_cd(level=9)))
    return markup