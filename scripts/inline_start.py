from aiogram.types import InlineQuery, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from aiogram import enums
from utils.my_utils import *
from uuid import uuid4
import time
import codext


async def main(inline_query: InlineQuery):
    word = inline_index(inline_query, 0)
    word = word.lower()
    user: User = inline_query.from_user
    user_id = str(user.id)

    if word.count(".") == 1:
        game_id = word
    else:
        game_id = None
   
    inline_button_text = ""
    if game_id:
        existing_game = my_database.exist_game(game_id)
        if existing_game:
            button_text = "Нужно ввести имя существительное, а не только число."
            message_text = f"<i>Я хотел продолжить, но не подобрал слов.</i>"
            inline_button_title = "Начать новую игру"
        else:
            button_text = "Такой игры нет."
            message_text = f"<i>Я хотел продолжить непонятно какую игру.</i>"
            inline_button_title = "Начать новую игру"
        
    else:
        type_word = await check_word(word)
        if type_word != "сущ":
            if type_word is None:
                type_word = "не существует"
            button_text = "Нужно ввести имя существительное."
            message_text = f"<i>Я хотел начать игру со слова {word}, но это {type_word}</i>"
            inline_button_title = "Начать вместо него"
        else:
            game_uid = str(round(time.time())) + "." + str(user.id)
            my_database.create_game(game_uid, f"{user_id}*{word}")

            button_text = f"Нажмите чтобы начать игру со слова «{word}»."
            message_text = f"<i><b>Я начал игру! Моё слово: {word}</b></i>"
            inline_button_title = "Продолжить"
            inline_button_text = f"{game_uid} {user_id}*{word} "
    
    inline_button = create_inline_button(inline_button_title, inline_button_text)
    delete_button = create_inline_button("Удалить игру", f"{game_uid} delete")
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button, delete_button]])
    
    button_id = str(uuid4())
    input_message_content = InputTextMessageContent(message_text=message_text, parse_mode=enums.ParseMode.HTML)
    
    result = InlineQueryResultArticle(id=button_id, title=button_text, input_message_content=input_message_content, 
    reply_markup=reply_markup)
    await inline_query.answer([result], cache_time=1, is_personal=True)
