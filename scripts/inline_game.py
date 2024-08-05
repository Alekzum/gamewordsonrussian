from aiogram.types import InlineQuery, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, User
from aiogram import enums, Bot
from uuid import uuid4
import logging
from importlib import reload
from utils import database as my_database, my_utils


my_database, my_utils = reload(my_database), reload(my_utils)


async def main(inline_query: InlineQuery):
    game_uid_and_user, word = inline_query.query.split(" ")
    word = word.lower()  # Обязательно!

    game_uid = game_uid_and_user

    user: User = inline_query.from_user
    user_id = str(user.id)

    existing_game = my_database.exist_game(game_uid_and_user)
    
    title = ""
    inline_button_title = ""
    inline_button_text = f"{game_uid} "
    inline_button_callback = None
    button_id = ""

    if not existing_game:
        return
    
    elif not my_utils.inline_valid(inline_query):
        title = "Ошибка в запросе"
        description = "Неверный формат запроса"
        message_text = f"<i>Я попробовал что-то неправильно сделать, но не получилось.</i>"
        inline_button_title = "Начать новую игру"
    
    elif existing_game:
        next_user = my_database.get_next_user(game_uid)
        user_is_next = user_id == next_user

        is_new_user = my_database.is_new_user(game_uid, user_id)
        already_given = my_database.is_in_game(game_uid, word)
        type_word = await my_utils.check_word(word)
        last_letter = my_database.get_last_letter(game_uid)

        if not(user_is_next or is_new_user):
            user_mention = f'{next_user} ( tg://user?id={next_user} ) '
            
            title = "Не ваша очередь"
            description = "Сейчас не ваша очередь."
            message_text = f'<i>{user_mention}, подъём. Я попытался продолжить вне своей очереди.</i>'
            inline_button_title = "Продолжить"
        
        elif already_given:
            title = "Ошибка"
            description = "Это слово уже было"
            message_text = f"<i>Я хотел продолжить словом <u>{word}</u>,  но оно уже было.</i>"
            inline_button_title = "Предложить другое слово"

        elif type_word != "сущ":
            title = "Ошибка"
            description = "Нужно ввести имя существительное."
            message_text = f"<i>Я хотел продолжить словом <u>{word}</u>, но это {type_word}</i>"
            inline_button_title = "Предложить другое слово"

        # elif type_word != "сущ":
        #     inline_button_title = "Ошибка"
        #     description = "Нужно ввести имя существительное."
        #     message_text = f"<i>Я хотел продолжить словом <u>{word}</u>, но это {type_word}</i>"

        elif word[0] != last_letter:
            title = "Ошибка"
            description = f"Нужно ввести слово, которое начинается на букву «{last_letter}»"
            message_text = (f"<i>Я хотел продолжить, но слово <u>{word}</u> не начинается на букву «{last_letter}»</i>")
            inline_button_title = "Продолжить другим словом"

        elif word[0] == last_letter:
            button_id = f"{game_uid} {user_id}*{word}"
            description = f"Продолжить словом {word}"
            message_text = f"<i>Я продолжаю игру словом <u>{word}</u>.</i>"
            inline_button_title = ""
            # inline_button_callback = f"{game_uid} {user_id}*{word}"
        
        else:
            title = "Неизвестная ошибка"
            description = "Я не ожидал такой случай..."
            message_text = (f"<i>Я хотел продолжить, что-то пошло не так</i>")


    else:
        # no_answer = True
        description = "Этой игры нет."
        message_text = "<i>Я хотел продолжить игру, которой нет.</i>"
        inline_button_title = "Начать новую игру"
        inline_button_text = " "

        
    # if inline_button_callback:
    #     inline_button = my_utils.create_inline_button(inline_button_title, callback=inline_button_callback)
    # else:
    inline_button = my_utils.create_inline_button(inline_button_title, inline_query=inline_button_text) if inline_button_title else None

    delete_button = my_utils.create_inline_button("Удалить игру", callback=f"{game_uid_and_user} delete")
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button], [delete_button]]) if inline_button else InlineKeyboardMarkup(inline_keyboard=[[delete_button]])

    button_id = button_id or str(uuid4())
    input_message_content = InputTextMessageContent(
        message_text=message_text, 
        parse_mode=enums.ParseMode.HTML
    )

    result = InlineQueryResultArticle(
        id=button_id, 
        title=title or description[:5]+"…", 
        description=description,
        input_message_content=input_message_content, 
        reply_markup=reply_markup
    )

    try:
        await inline_query.answer([result], cache_time=1, is_personal=True)

    except Exception as ex:
        ex_str = str(ex)
        description = f"Произошла ошибка: {ex_str}."
        message_text = f"<i>Я хотел продолжить игру, но словил ошибку {ex_str}.</i>"
        inline_button_title = "Начать новую игру"

        inline_button = my_utils.create_inline_button(inline_button_title, "")
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

        button_id = str(uuid4())
        input_message_content = InputTextMessageContent(
            message_text=message_text, 
            parse_mode=enums.ParseMode.HTML
        )
        
        result = InlineQueryResultArticle(
            id=button_id, 
            title=description,
            input_message_content=input_message_content, 
            reply_markup=reply_markup
        )
            
        await inline_query.answer([result], cache_time=1, is_personal=True)
