import asyncio
import datetime

import aioschedule

from data.config import admins
from loader import bot
from utils.db_api.commands import get_today_hours, get_user_by_id, delete_record, add_record_history, delete_day


async def scheduler():
    aioschedule.every().day.at("05:45").do(today_records)
    aioschedule.every().day.at("21:50").do(transfer_records)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def first_start():
    await asyncio.create_task(scheduler())


async def today_records():
    year, month, day = list(map(int, datetime.datetime.now().strftime("%Y/%m/%d").split("/")))
    records = await get_today_hours(year=year, month=month, day=day)
    message_text = f"Записи на сегодня: {day}/{month}/{year}\n" \
                   f"{'-' * 35}\n"
    for record in records:
        if record.user_reserved is None:
            continue
        user = await get_user_by_id(user_id=record.user_reserved)
        user_full_name = f"{user.first_name} {user.last_name if user.last_name else ''}"
        message_text += f"<b>{record.start_hour}</b>\n" \
                        f"Клиент:\n" \
                        f"{user_full_name} {'@' + user.login if user.login else ''}\n\n" \
                        f"Информация по записи:\n" \
                        f"{record.description}\n" \
                        f"{'-' * 35}\n"
        try:
            await bot.send_message(text=f"Доброе утро, {user.first_name}! Согласно расписанию, вы записаны на сегодня: "
                                        f"<b>{day}/{month}/{year} - {record.start_hour}</b>\n"
                                        f"Если возникла ошибка, вы можете отменить запись через Личный кабинет.",
                                   chat_id=user.user_id)
            await asyncio.sleep(3)
        except:
            await bot.send_message(text=f"Не получилось отправить уведомление клиенту "
                                        f"{user_full_name} {'@' + user.login if user.login else ''}",
                                   chat_id=admins[0])
            await asyncio.sleep(1)
    message = await bot.send_message(text=message_text, chat_id=admins[0])
    try:
        await bot.unpin_all_chat_messages(chat_id=admins[0])
    except:
        pass
    try:
        await bot.pin_chat_message(chat_id=admins[0], message_id=message.message_id)
    except:
        pass


async def transfer_records():
    year, month, day = list(map(int, datetime.datetime.now().strftime("%Y/%m/%d").split("/")))
    records = await get_today_hours(year=year, month=month, day=day)
    for record in records:
        await add_record_history(
            user_id=record.user_reserved,
            date=record.date,
            start_hour=record.start_hour,
            description=record.description,
            comment=record.comment
        )
        await delete_record(hour_id=record.id)
    await delete_day(day=day, month=month, year=year)


loop = asyncio.get_event_loop()
loop.create_task(first_start())
