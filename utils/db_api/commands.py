from typing import List

from sqlalchemy import and_
from gino import Gino

from utils.db_api.models import History, OpenDays, OpenHours, Users

db = Gino()


async def get_months(year):
    return [_.month for _ in await OpenDays.query.distinct(OpenDays.month).where(
        and_(
            OpenDays.year == year,
            OpenDays.available == True
        )
    ).gino.all()]


async def get_free_days(year, month, day):
    return [_.day for _ in await OpenDays.query.distinct(OpenDays.day).where(
        and_(
            OpenDays.available == True,
            OpenDays.year == year,
            OpenDays.month == month,
            OpenDays.day != day,
        )
    ).gino.all()
            ]


async def get_all_days(year, month):
    return [_.day for _ in await OpenDays.query.distinct(OpenDays.day).where(
        and_(
            OpenDays.year == year,
            OpenDays.month == month,
        )
    ).gino.all()
            ]


async def get_today_hours(year, month, day):
    return [_ for _ in await OpenHours.query.distinct(OpenHours.start_hour).where(
        OpenHours.date == f"{day}/{month}/{year}").gino.all()]


async def get_hours(year, month, day):
    return await OpenHours.query.distinct(OpenHours.start_hour).where(
        and_(
            OpenHours.date == f"{day}/{month}/{year}",
            OpenHours.reserved == False,
        )
    ).gino.all()


async def get_hour_by_id(hour_id):
    return await OpenHours.query.where(OpenHours.id == hour_id).gino.first()


async def get_user_by_id(user_id):
    return await Users.query.where(Users.user_id == user_id).gino.first()


async def get_users_records(year, month, day) -> List[OpenHours]:
    return await OpenHours.query.where(OpenHours.date == f"{day}/{month}/{year}").gino.all()


async def get_history_records(year, month, day) -> List[History]:
    return await History.query.distinct(History.start_hour).where(
        History.date == f"{day}/{month}/{year}").gino.all()


async def get_user_record(user_id):
    return await OpenHours.query.where(OpenHours.user_reserved == user_id).gino.all()


async def get_user_history(user_id):
    return await History.query.where(History.user_id == user_id).gino.all()


async def get_history_by_id(history_id):
    return await History.query.where(History.id == history_id).gino.first()


async def count_reserve_records(year, month, day):
    return await db.select([db.func.count()]).where(
        and_(
            OpenHours.date == f"{day}/{month}/{year}",
            OpenHours.reserved == True,
        )
    ).gino.scalar()


async def count_history_records(year, month, day):
    return await db.select([db.func.count()]).where(
        and_(
            History.date == f"{day}/{month}/{year}",
            History.user_id != None,
        )
    ).gino.scalar()


async def update_record(hour_id, user_reserved, description):
    obj = await get_hour_by_id(hour_id=hour_id)
    await obj.update(reserved=True, user_reserved=user_reserved, description=description).apply()
    day, month, year = obj.date.split("/")
    await update_day_status(day=day, month=month, year=year)


async def cancel_record(hour_id):
    obj = await get_hour_by_id(hour_id=hour_id)
    await obj.update(
        description=None,
        comment=None,
        reserved=False,
        user_reserved=None,
    ).apply()


async def update_day_status(day, month, year):
    day_obj = await OpenDays.query.where(
        and_(
            OpenDays.day == int(day),
            OpenDays.month == int(month),
            OpenDays.year == int(year),
        )
    ).gino.first()
    if await check_available_hours(date=f"{int(day)}/{int(month)}/{year}"):
        await day_obj.update(available=True).apply()
    else:
        await day_obj.update(available=False).apply()


async def check_available_hours(date):
    obj = await OpenHours.query.where(
        and_(
            OpenHours.date == date,
            OpenHours.reserved == False,
        )
    ).gino.all()
    if len(obj) > 0:
        return True
    else:
        return False


async def add_record(**kwargs):
    return await OpenHours(**kwargs).create()


async def add_day(**kwargs):
    return await OpenDays(**kwargs).create()


async def add_user(**kwargs):
    return await Users(**kwargs).create()


async def add_record_history(**kwargs):
    return await History(**kwargs).create()


async def add_record_comment(hour_id, record_comment):
    obj = await get_hour_by_id(hour_id=hour_id)
    await obj.update(comment=record_comment).apply()


async def delete_record(hour_id):
    return await OpenHours.delete.where(OpenHours.id == hour_id).gino.status()


async def delete_day(day, month, year):
    return await OpenDays.delete.where(
        and_(
            OpenDays.day == int(day),
            OpenDays.month == int(month),
            OpenDays.year == int(year),
        )
    ).gino.status()
