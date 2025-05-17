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

price = "Прайс:\n"\
        "<b>Действует c 1.05.2025</b>\n\n"\
        "-Классика: 1600₽\n"\
        "-Уголки: 1300₽\n"\
        "-1,5D: 1800₽\n"\
        "-2D: 2000₽\n"\
        "-2,5D: 2200₽\n"\
        "-3D, Anime: 2400₽\n"\
        "-Мокрый эффект, Princess, Butterfly, Revival: 2100₽\n"\
        "-Нижние ресницы: +500₽\n"\
        "-Цветные ресницы, лучи: +200₽\n"\
        "-Снятие не моей работы: 200₽\n"\
        "-Снятие моей работы с последующим наращиванием: БЕСПЛАТНО\n"\
        "-Без последующего наращивания: 300₽\n"

redis = {
    'address': (ip, 6379),
    'encoding': 'utf8'
}
POSTGRES_URI = f'postgresql://{pguser}:{pgpassword}@{ip}/{DATABASE}'
