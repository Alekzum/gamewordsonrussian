from utils import database as my_database, my_utils
from aiogram.types import ChosenInlineResult, InlineKeyboardMarkup
from aiogram import enums



async def main(cir: ChosenInlineResult):
    async def answer(inline_message_id="0", _text="", _reply_markup=None):
        # await callback_query.answer()
        return await cir.bot.edit_message_text(
            _text, 
            inline_message_id=cir.inline_message_id, 
            reply_markup=_reply_markup, 
            parse_mode=enums.ParseMode.HTML
        )
    uid = cir.result_id

    match uid.split():
        case [game_uid, uid_and_word]:
            inline_button = my_utils.create_inline_button("Играть", inline_query=f"{game_uid} ")
            delete_button = my_utils.create_inline_button("Хочу удалить игру.", callback=f"{game_uid} delete")
            inline_message_id = cir.inline_message_id

            if uid_and_word.count("*") == 1:
                user_id, word = uid_and_word.split("*")
                next_id = my_database.get_next_user(game_uid)

                if user_id == next_id or my_database.is_new_user(game_uid, user_id):
                    my_database.append_word(game_uid, uid_and_word)
                    my_database.append_message(game_uid, inline_message_id)
                    text = f"<i>{user_id} продолжил словом <u>{word}</u>. "
                
                else:
                    last_act = my_database.get_last_act(game_uid)
                    word = last_act[list(last_act.keys())[0]]
                    text = f"<i>{user_id} хотел пойти вне своей очереди. "

                next_id = my_database.get_next_user(game_uid)
                players = ", ".join(my_database.get_users(game_uid)).replace(next_id, f"<u>{next_id}</u>")
                words = ", ".join(my_database.get_words(game_uid))
                next_letter = word[-1] if word[-1] not in 'ьыъ' else word[-2]
                text += f"Следующее слово должно быть на «{next_letter}»</i>\nТекущий распорядок игроков: {players}\nСписок использованных слов в игре: {words}"
                reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button, delete_button]])
                await answer(inline_message_id, text, reply_markup)
