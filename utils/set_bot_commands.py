from aiogram import types

from data.config import admins


async def set_default_commands(dp):
    await dp.bot.set_my_commands([types.BotCommand("start", "Запуск бота")])


async def set_admin_commands(dp):
    await dp.bot.set_my_commands(
        commands = [
            types.BotCommand("start", "Запуск бота"),
            types.BotCommand("admin_login", "Панель администратора"),
        ],
        scope=types.BotCommandScopeChat(chat_id=admins[0])
    )
