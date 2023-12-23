from aiogram.types import CallbackQuery
from importlib import reload

from utils import database as my_database
my_database = reload(my_database)

async def main(callback_query: CallbackQuery):
    game_uid, word = callback_query.data.split(" ")
    inline_uid, creator_uid = game_uid.split(".")
    
    user_id = str(callback_query.from_user.id)
    
    if my_database.exist_game(game_uid):
        if word == "delete" and creator_uid == user_id:
            my_database.delete_game(game_uid)
            await callback_query.answer("Игра удалена!", show_alert=True)
        elif word == "delete":
            await callback_query.answer("Вы не создатель этой игры.")
        else:
            await callback_query.answer("Ачё мне прислали?")
    else:
        await callback_query.answer("Этой игры уже нет")
