from aiogram.types import InlineQuery, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from aiogram import enums
from utils.my_utils import *
from uuid import uuid4
import codext


async def main(inline_query: InlineQuery):
    game_id, word = inline_query.query.split(" ")
    
    user: User = inline_query.from_user
    user_id = str(user.id)
    mention = user.mention_html()

    if game_id.count(".") == 1:
        game_uid, user_uid = game_id.split(".")
    else:
        return
    
    if word != "delete":
        return
    
    inline_button_text = ""
    if game_id:
        existing_game = my_database.exist_game(game_id)
        if existing_game and user_uid == user_id:
            button_text = "Хочешь удалить игру? Не забудь потом на кнопку под сообщением нажать."
            message_text = f"<i>Хочу удалить игру. Осталось только на кнопку нажать…</i>"
            inline_button_title = "Удалить игру 😨"
            callback = f"{game_id} delete"
        else:
            return
    
    inline_button = InlineKeyboardButton(text=inline_button_title, callback_data=callback)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])
    
    button_id = str(uuid4())
    input_message_content = InputTextMessageContent(message_text=message_text, parse_mode=enums.ParseMode.HTML)
    
    result = InlineQueryResultArticle(id=button_id, title=button_text, input_message_content=input_message_content, 
    reply_markup=reply_markup)
    await inline_query.answer([result], cache_time=1, is_personal=True)
