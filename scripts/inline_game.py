from aiogram.types import InlineQuery, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from utils.my_utils import *
from aiogram import enums
from uuid import uuid4
from importlib import reload

from utils import database as my_database
my_database = reload(my_database)


async def main(inline_query: InlineQuery):
    game_uid_and_user, prev_user_and_word, word = inline_query.query.split(" ")
    word = word.lower()
    
    if not my_database.exist_game(game_uid_and_user):
        return
        
    my_database.append_word(game_uid_and_user, prev_user_and_word)
    last_act = my_database.get_last_act(game_uid_and_user)
    current_act = {prev_user_and_word.split("*")[0]: prev_user_and_word.split("*")[1]}
    if last_act != current_act:
        print(last_act, current_act)
        return
    
    no_answer = False
    if game_uid_and_user.count(".") != 1 or prev_user_and_word.count("*") != 1:
        # no_answer = True
        button_text = "Неверный формат запроса…"
        message_text = f"<i>Я попробовал что-то сделать, но не получилось.</i>"
        inline_button = create_inline_button("Начать новую игру")
    my_database.append_word(game_uid_and_user, prev_user_and_word)
    
    prev_user, prev_word = prev_user_and_word.split("*")
    game_id, game_creator_id = game_uid_and_user.split(".")
    game_uid = game_uid_and_user

    user: User = inline_query.from_user
    user_id = str(user.id)
    mention = user.mention_html()
    
    inline_button_text = ""
    existing_game = my_database.exist_game(game_uid_and_user)

    if existing_game:
        next_user = my_database.get_next_user(game_uid)
        if next_user == user_id or my_database.is_new_user(game_uid, user_id):
            already_given = my_database.is_in_game(game_uid, word)
            if already_given:
                button_text = "Это слово уже было"
                message_text = f"<i>Я хотел продолжить словом «{word}», но оно уже было.</i>"
                inline_button_title = "Продолжить"
                inline_button_text = f"{game_uid} {prev_user_and_word}"
            else:
                type_word = await check_word(word)
                if type_word != "сущ":
                    button_text = "Нужно ввести имя существительное."
                    message_text = f"<i>Я хотел продолжить словом «{word}», но это {type_word}</i>"
                    inline_button_title = "Начать игру"
                else:
                    last_word = my_database.get_last_word(game_uid)
                    last_letter = last_word[-1]
                    if last_letter in ["ъ", "ь", "ы"]:
                        last_letter = last_word[-2]
                    if word[0] == last_letter:
                        last_letter_new_word = word[-1]
                        button_text = f"Продолжить словом {word}"
                        message_text = (f"<i>Я продолжаю игру словом {word}.</i>")
                        inline_button_title = "Продолжить"
                        inline_button_text = f"{game_uid} {user_id}*{word}"
                    else:
                        button_text = f"Нужно ввести слово, которое начинается на букву «{last_letter}»"
                        message_text = f"<i>Я хотел продолжить, но слово «{word}» не начинается на букву «{last_letter}»</i>"
                        inline_button_title = "Продолжить вместо него"
                        inline_button_text = f"{game_uid} {user_id}*{word}"
        else:
            # no_answer = True
            # help(inline_query)
            # next_user_mention = (await client.get_user(int(next_user))).mention()
            button_text = "Сейчас не ваша очередь."
            message_text = f"<i>{next_user}, подъём. Я попытался продолжить вне своей очереди.</i>"
            inline_button_title = "Продолжить"
            inline_button_text = f"{game_uid}"
        
        
    else:
        # no_answer = True
        button_text = "Этой игры нет."
        message_text = "<i>Я хотел продолжить игру, которой нет.</i>"
        inline_button_title = "Начать новую игру"
    
    if no_answer:
        return
    inline_button_text += " "
    inline_button = create_inline_button(inline_button_title, inline_button_text)
    delete_button = InlineKeyboardButton(text="Удалить игру", callback_data=f"{game_uid_and_user} delete")
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button, delete_button]])
    
    button_id = str(uuid4())
    input_message_content = InputTextMessageContent(message_text=message_text, parse_mode=enums.ParseMode.HTML)
    result = InlineQueryResultArticle(
    id=button_id, title=button_text, input_message_content=input_message_content, reply_markup=reply_markup)
    await inline_query.answer([result], cache_time=1, is_personal=True)
