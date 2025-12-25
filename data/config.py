import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

pguser = str(os.getenv("pguser"))
pgpassword = str(os.getenv("pgpassword"))
DATABASE = str(os.getenv("DATABASE"))
admin_id = str(os.getenv("admin_id"))

ip = os.getenv("ip")

aiogram_redis = {
    'host': ip,
}
month_ru = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}

admins = [admin_id]



redis = {
    'address': (ip, 6379),
    'encoding': 'utf8'
}
POSTGRES_URI = f'postgresql://{pguser}:{pgpassword}@{ip}/{DATABASE}'
