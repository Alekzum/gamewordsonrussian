from aiogram.types import InlineQuery, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, User
from aiogram import enums, Bot
from uuid import uuid4
import time

from importlib import reload
from utils import database as my_database, my_utils

my_database, my_utils = reload(my_database), reload(my_utils)


async def main(inline_query: InlineQuery):
    word = inline_query.query
    word = word.lower()

    user: User = inline_query.from_user
    user_id = str(user.id)

    if word.count(".") == 1:
        game_uid = word
    else:
        game_uid = None

    button_callback = None
    button_inline = ""
    delete_button = None
    button_id = 0

    if game_uid:
        existing_game = my_database.exist_game(game_uid)
        if existing_game:
            next_user = my_database.get_next_user(game_uid)
            if user_id == next_user:
                last_letter = my_database.get_last_letter(game_uid)
                button_text = f"Нужно ввести слово на букву «{last_letter}»."
                message_text = f"<i>Я хотел продолжить, но не подобрал слов.</i>"
                button_title = "Продолжить игру"
                button_inline = f"{game_uid} "
                delete_button = my_utils.create_inline_button("Удалить игру", callback=f"{game_uid} delete")
            else:
                user_mention = f'{next_user} ( tg://user?id={next_user} ) '
                button_text = "Сейчас не ваша очередь."
                message_text = f'<i>{user_mention}, подъём. Я попытался продолжить вне своей очереди.</i>'
                button_title = "Продолжить"
                button_inline = f"{game_uid} "
                
        else:
            button_text = "Такой игры нет."
            message_text = f"<i>Я хотел продолжить непонятно какую игру.</i>"
            button_title = "Начать новую игру"

    else:
        type_word = await my_utils.check_word(word)
        if type_word != "сущ":
            if type_word is None:
                type_word = "не существует"
            button_text = "Нужно ввести имя существительное."
            message_text = f"<i>Я хотел начать игру со слова {word}, но это {type_word}</i>"
            button_title = "Начать игру"
        else:
            game_uid = str(round(time.time())) + "." + user_id
            my_database.create_game(game_uid, f"{user_id}*{word}")

            button_id = f"{game_uid} {user_id}*{word}"
            button_text = f"Нажмите чтобы начать игру со слова «{word}»."
            message_text = f"<i><b>Я начал игру! Моё слово: <u>{word}</u></b></i>"
            button_title = ""
            # button_callback = f"{game_uid} {user_id}*{word}"
            delete_button = my_utils.create_inline_button("Удалить игру", callback=f"{game_uid} delete")

    if not button_title:
        inline_button = None
    if button_callback:
        inline_button = my_utils.create_inline_button(button_title, callback=button_callback)
    else:
        inline_button = my_utils.create_inline_button(button_title, button_inline)

    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button, delete_button] if (inline_button and delete_button) else [delete_button] if delete_button else [inline_button]])
    button_id = button_id or str(uuid4())

    input_message_content = InputTextMessageContent(message_text=message_text, parse_mode=enums.ParseMode.HTML)

    result = InlineQueryResultArticle(
        id=button_id, 
        title=button_text[:5]+"…", 
        description=button_text,
        input_message_content=input_message_content, 
        reply_markup=reply_markup
    )
    
    try:
        await inline_query.answer([result], cache_time=1, is_personal=True)
    except Exception as ex:
        ex_str = str(ex)
        button_text = f"Произошла ошибка: {ex_str}."
        message_text = f"<i>Я хотел начать игру, но словил ошибку{ex_str}.</i>"
        button_title = "Начать новую игру"

        inline_button = my_utils.create_inline_button(button_title, "")
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

        button_id = str(uuid4())
        input_message_content = InputTextMessageContent(message_text=message_text, parse_mode=enums.ParseMode.HTML)
        result = InlineQueryResultArticle(
            id=button_id, title=button_text, input_message_content=input_message_content, reply_markup=reply_markup)
        await inline_query.answer([result], cache_time=1, is_personal=True)
