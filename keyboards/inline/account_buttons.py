from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from utils.db_api.commands import get_user_history

user_menu_cd = CallbackData("user_menu", "level", "hour_id", "user_id", "history_id", "page")
user_history_cd = CallbackData("user_menu", "level", "hour_id", "user_id")


def make_user_menu_cd(level=0, hour_id=0, user_id=0, history_id=0, page=0):
    return user_menu_cd.new(
        level=level,
        hour_id=hour_id,
        user_id=user_id,
        history_id=history_id,
        page=page
    )


async def user_options():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Активная запись", callback_data="user_record"))
    markup.row(InlineKeyboardButton(text="История записей", callback_data="user_history"))
    # markup.row(InlineKeyboardButton(text="Управление уведомлениями", callback_data="notification"))
    return markup


async def user_record_keyboard(hour_id):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Отменить запись",
                                    callback_data=make_user_menu_cd(
                                        level=CURRENT_LEVEL + 1,
                                        hour_id=hour_id)
                                    )
               )
    # markup.row(InlineKeyboardButton(text="Изменить запись",
    #                                 callback_data=make_user_menu_cd(
    #                                     level=None,
    #                                     hour_id=hour_id)
    #                                 )
    #            )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_user_menu_cd(level=CURRENT_LEVEL - 1)
                                    )
               )
    return markup


async def check_user_record_cancel_keyboard(hour_id):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Продолжить",
                                    callback_data=make_user_menu_cd(level=CURRENT_LEVEL + 1,
                                                                    hour_id=hour_id)
                                    )
               )
    markup.row(InlineKeyboardButton(text="Назад",
                                    callback_data=make_user_menu_cd(level=CURRENT_LEVEL - 1,
                                                                    hour_id=hour_id)
                                    )
               )
    return markup


async def user_history_keyboard(user_id, page):
    markup = InlineKeyboardMarkup(row_width=1)
    CURRENT_LEVEL = 4
    MAX_RECORDS_PER_PAGE = 10

    records = await get_user_history(user_id)

    first_order_index = (page - 1) * MAX_RECORDS_PER_PAGE
    last_order_index = page * MAX_RECORDS_PER_PAGE
    sliced_array = records[first_order_index:last_order_index]

    for record in sliced_array:
        button_text = f"{record.date} - {record.start_hour}"
        callback_data = make_user_menu_cd(level=CURRENT_LEVEL + 1,
                                          page=page,
                                          history_id=record.id)
        markup.insert(InlineKeyboardMarkup(text=button_text, callback_data=callback_data))

    pages_buttons = list()
    if len(records) % MAX_RECORDS_PER_PAGE == 0:
        max_page = len(records) // MAX_RECORDS_PER_PAGE
    else:
        max_page = len(records) // MAX_RECORDS_PER_PAGE + 1

    previous_page = page - 1
    if previous_page >= 1:
        previous_page_text = "⬅"
        pages_buttons.append(
            InlineKeyboardButton(text=previous_page_text,
                                 callback_data=make_user_menu_cd(level=CURRENT_LEVEL,
                                                                 page=previous_page,
                                                                 user_id=user_id)
                                 )
        )

    pages_buttons.append(
        InlineKeyboardButton(
            text=f"{page} из {max_page}",
            callback_data=make_user_menu_cd(level=CURRENT_LEVEL,
                                            page=page,
                                            user_id=user_id)
        )
    )

    next_page = page + 1
    if next_page <= max_page:
        next_page_text = "➡"
        pages_buttons.append(
            InlineKeyboardButton(text=next_page_text,
                                 callback_data=make_user_menu_cd(level=CURRENT_LEVEL,
                                                                 page=next_page,
                                                                 user_id=user_id)
                                 )
        )

    markup.row(*pages_buttons)
    markup.row(InlineKeyboardButton(
        text="Назад",
        callback_data=make_user_menu_cd(level=0)
    ))
    return markup


async def user_history_back_keyboard(page: int):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(
        text="Назад",
        callback_data=make_user_menu_cd(level=4,
                                        page=page)
    ))
    return markup
