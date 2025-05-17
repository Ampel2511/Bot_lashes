from aiogram import types
from aiogram.dispatcher import FSMContext


async def cancel(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    await callback.answer("Вы закрыли меню", show_alert=True)
    await callback.message.edit_reply_markup()
    await state.finish()
