from aiogram.types import InlineQuery, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, User
from aiogram import enums, Bot
from uuid import uuid4
import logging

from importlib import reload
from utils import database as my_database, my_utils

my_database, my_utils = reload(my_database), reload(my_utils)


async def main(bot: Bot, inline_query: InlineQuery):
    game_uid_and_user, word = inline_query.query.split(" ")
    word = word.lower()  # Обязательно!

    game_uid = game_uid_and_user

    user: User = inline_query.from_user
    user_id = str(user.id)

    existing_game = my_database.exist_game(game_uid_and_user)
    inline_button_text = ""
    inline_button_callback = None
    if not existing_game:
        return
    elif not my_utils.inline_valid(inline_query):
        inline_button_title = "Начать новую игру"
        button_text = "Неверный формат запроса…"
        message_text = f"<i>Я попробовал что-то сделать, но не получилось.</i>"
    elif existing_game:
        next_user = my_database.get_next_user(game_uid)
        if next_user == user_id or my_database.is_new_user(game_uid, user_id):
            already_given = my_database.is_in_game(game_uid, word)
            if already_given:
                button_text = "Это слово уже было"
                message_text = f"<i>Я хотел продолжить словом <u>{word}</u>,  но оно уже было.</i>"
                inline_button_title = "Продолжить"
                inline_button_text = f"{game_uid} "
            else:
                type_word = await my_utils.check_word(word)
                if type_word != "сущ":
                    button_text = "Нужно ввести имя существительное."
                    message_text = f"<i>Я хотел продолжить словом <u>{word}</u>, но это {type_word}</i>"
                    inline_button_title = "Продолжить вместо него"
                    inline_button_text = f"{game_uid} "
                else:
                    last_word = my_database.get_last_word(game_uid)
                    last_letter = last_word[-1]
                    if last_letter in ["ъ", "ь", "ы"]:
                        last_letter = last_word[-2]
                    if word[0] == last_letter:
                        button_text = f"Продолжить словом {word}"
                        message_text = f"<i>Я продолжаю игру словом <u>{word}</u>.</i>"
                        inline_button_title = "Продолжить"
                        inline_button_callback = f"{game_uid} {user_id}*{word}"
                    else:
                        button_text = f"Нужно ввести слово, которое начинается на букву «{last_letter}»"
                        message_text = (f"<i>Я хотел продолжить, но слово <u>{word}</u> не начинается на букву"
                                        f"«{last_letter}»</i>")
                        inline_button_title = "Продолжить вместо него"
                        inline_button_text = f"{game_uid} "
        else:
            user_mention = f'{next_user} ( tg://user?id={next_user} ) '
            button_text = "Сейчас не ваша очередь."
            message_text = f'<i>{user_mention}, подъём. Я попытался продолжить вне своей очереди.</i>'
            inline_button_title = "Продолжить"
            inline_button_text = f"{game_uid} "
    else:
        # no_answer = True
        button_text = "Этой игры нет."
        message_text = "<i>Я хотел продолжить игру, которой нет.</i>"
        inline_button_title = "Начать новую игру"
    if inline_button_callback:
        inline_button = my_utils.create_inline_button(inline_button_title, callback=inline_button_callback)
    else:
        inline_button = my_utils.create_inline_button(inline_button_title, inline_query=inline_button_text)
    delete_button = my_utils.create_inline_button("Удалить игру", callback=f"{game_uid_and_user} delete")
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button, delete_button]])

    button_id = str(uuid4())
    input_message_content = InputTextMessageContent(message_text=message_text, parse_mode=enums.ParseMode.HTML)
    result = InlineQueryResultArticle(id=button_id, title=button_text[:5]+"…", description=button_text,
                                      input_message_content=input_message_content, reply_markup=reply_markup)
    try:
        await inline_query.answer([result], cache_time=1, is_personal=True)
    except Exception as ex:
        ex_str = str(ex)
        button_text = f"Произошла ошибка: {ex_str}."
        message_text = f"<i>Я хотел продолжить игру, но словил ошибку {ex_str}.</i>"
        inline_button_title = "Начать новую игру"

        inline_button = my_utils.create_inline_button(inline_button_title, "")
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

        button_id = str(uuid4())
        input_message_content = InputTextMessageContent(message_text=message_text, parse_mode=enums.ParseMode.HTML)
        result = InlineQueryResultArticle(
            id=button_id, title=button_text, input_message_content=input_message_content, reply_markup=reply_markup)
        await inline_query.answer([result], cache_time=1, is_personal=True)
