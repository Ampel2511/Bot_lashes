import datetime
from aiogram import types
# from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from handlers.users.about import about_info
from handlers.users.dates import list_months
from handlers.users.price import lashes_price
from handlers.users.user_account import account_user
from keyboards.default import user_menu
from loader import dp, bot
from utils.misc import rate_limit


@rate_limit(limit=5)
@dp.message_handler(CommandStart())
async def check_user(message: types.Message,
                     # state: FSMContext
                     ):
    await bot_start(message=message)
    # if await get_user_by_id(user_id=message.from_user.id):
    #     await bot_start(message=message)
    # else:
    #     captcha_img, pattern = await create_new_captcha()
    #     captcha_img.write(pattern, f"{pattern}.png")
    #     await message.answer_photo(photo=InputFile(path_or_bytesio=f"{pattern}.png"),
    #                                caption='Решите капчу')
    #     os.remove(f"{pattern}.png")
    #     await state.set_state('get_captcha')
    #     await state.update_data(captcha=pattern)


# @dp.message_handler(state='get_captcha')
# async def get_captcha(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     if message.text == data['captcha']:
#         await state.finish()
#         await bot_start(message=message)
#     else:
#         captcha_img, pattern = await create_new_captcha()
#         captcha_img.write(pattern, f"{pattern}.png")
#         await message.answer_photo(photo=InputFile(path_or_bytesio=f"{pattern}.png"),
#                                    caption='Неверная капча, попробуйте снова.')
#         os.remove(f"{pattern}.png")
#         await state.update_data(captcha=pattern)


async def bot_start(message: types.Message):
    await message.answer(text=f"Здравствуйте, {message.from_user.first_name}\n"
                              f"Добро пожаловать в {(await bot.me).username}\n"
                              f"Используя кнопочное меню, выберите необходимое ⬇",
                         reply_markup=user_menu
                         )


@dp.message_handler(text="Записаться 📝")
async def choose_month(message: types.Message):
    now = datetime.datetime.now()
    await list_months(message=message, year=now.year)


@dp.message_handler(text="Личный кабинет 💼")
async def open_user_account(message: types.Message):
    await account_user(message=message)


@dp.message_handler(text="Отзывы 🗣")
async def reviews(message: types.Message):
    pass


@dp.message_handler(text="Прайс 💸")
async def price(message: types.Message):
    await lashes_price(message=message)


@dp.message_handler(text="О нас ℹ️")
async def about(message: types.Message):
    await about_info(message=message)
