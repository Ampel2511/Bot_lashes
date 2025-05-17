from loader import bot
from utils.redis.start_funcs import first_start
from utils.set_bot_commands import set_default_commands, set_admin_commands


async def on_shutdown(dp):
    await bot.close()


async def on_startup(dp):
    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)
    # await first_start()

    await set_default_commands(dp)
    await set_admin_commands(dp)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
