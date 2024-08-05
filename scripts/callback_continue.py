from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle
from aiogram import Bot, enums
from importlib import reload
from utils import database as my_database, my_utils
import asyncio


my_database, my_utils = reload(my_database), reload(my_utils)


async def main(callback_query: CallbackQuery):
    async def answer(inline_message_id="0", _text="", _reply_markup=None):
        await callback_query.answer()
        return await callback_query.bot.edit_message_text(
            _text, 
            inline_message_id=inline_message_id, 
            reply_markup=_reply_markup, 
            parse_mode=enums.ParseMode.HTML
        )
    
    # print(callback_query)
    game_uid, uid_and_word = callback_query.data.split(" ")
    creator_uid = game_uid.split(".")[1]

    message_inline_id: str = str(callback_query.inline_message_id)
    current_user_id = str(callback_query.from_user.id)

    if my_database.exist_game(game_uid):
        inline_button = my_utils.create_inline_button("Играть", inline_query=f"{game_uid} ")
        delete_button = my_utils.create_inline_button("Хочу удалить игру.", callback=f"{game_uid} delete")
        if uid_and_word == "delete" and creator_uid == current_user_id:
            text = "<i>Создатель игры хочет удалить игру.</i>"
            real_del_button = my_utils.create_inline_button("Реально удалить игру.", callback=f"{game_uid} real_delete")
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button, delete_button], [real_del_button]])
            await answer(message_inline_id, text, reply_markup)

        elif uid_and_word == "real_delete" and creator_uid == current_user_id:
            my_database.delete_game(game_uid)
            await callback_query.answer("Игра удалена.", show_alert=True)
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                text="Начать новую игру", switch_inline_query_current_chat="")]])
            await callback_query.bot.edit_message_text(inline_message_id=callback_query.inline_message_id, text="Игра удалена.",
                                        reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            for uid in my_database.get_messages(game_uid):
                await callback_query.bot.edit_message_text(inline_message_id=uid, text="Игра удалена :(")
            my_database.delete_messages(game_uid)

        elif uid_and_word in ["delete", "real_delete"]:
            await callback_query.answer("Вы не создатель этой игры.")

        elif uid_and_word.count("*") == 1:
            user_id, word = uid_and_word.split("*")
            next_id = my_database.get_next_user(game_uid)
            if user_id == next_id or my_database.is_new_user(game_uid, user_id):
                my_database.append_word(game_uid, uid_and_word)
                my_database.append_message(game_uid, message_inline_id)
                text = f"<i>{user_id} продолжил словом <u>{word}</u>. "
            else:
                last_act = my_database.get_last_act(game_uid)
                word = last_act[list(last_act.keys())[0]]
                text = f"<i>{user_id} хотел пойти вне своей очереди. "

            next_id = my_database.get_next_user(game_uid)
            players = ", ".join(my_database.get_users(game_uid)).replace(next_id, f"<u>{next_id}</u>")
            words = ", ".join(my_database.get_words(game_uid))
            text += (f"Следующее слово должно быть на «{word[-1] if word[-1] not in 'ьыъ' else word[-2]}»</i>\n"
                    f"Текущий распорядок игроков: {players}\n" f"Список использованных слов в игре: {words}")
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button], [delete_button]])
            await answer(message_inline_id, text, reply_markup)

        else:
            await callback_query.answer("А чё мне прислали?")
    else:
        await callback_query.answer("Этой игры уже нет")
        inline_button = my_utils.create_inline_button("Начать новую игру", inline_query="")
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])
        # await callback_query.bot.edit_message_reply_markup(inline_message_id=callback_query.inline_message_id, reply_markup=None)
        await callback_query.bot.edit_message_text(inline_message_id=callback_query.inline_message_id, text="Игра удалена :(")
        for uid in my_database.get_messages(game_uid) or []:
            await asyncio.sleep(0.5)
            await callback_query.bot.edit_message_text(inline_message_id=uid, text="Игра удалена :(")
        try: my_database.delete_messages(game_uid)
        except: pass
