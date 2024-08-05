from aiogram.types import InlineQuery, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from .config import DICT_API
import utils.database as my_database
import logging
import dotenv
import httpx
import json
import os
import re


censorFilePath = os.sep.join(['source', 'censor.txt'])
srcFilePath = os.sep.join(['source', 'src_words.json'])

httpx_client = httpx.AsyncClient()
rus_pattern = re.compile(r"([а-яА-Я]+)")
dictionary_search_logger = logging.getLogger("Yandex.Dict")


def inline_valid(inline_query: InlineQuery) -> bool:
    return (inline_query.query.count(".") == 1 and inline_query.query.count(" ") == 1 and
            re.fullmatch(rus_pattern, inline_query.query.split(" ")[1]))


def save_dict(dictionary: dict):
    with open(srcFilePath, "w", encoding="utf-8") as _get_word_file:
        json.dump(dictionary, _get_word_file, ensure_ascii=False, indent=4, sort_keys=True)

async def check_word(word: str) -> str:
    """Возвращает часть речи заданного слова или "мат" | "не существует"."""
    word = word.lower()

    if not rus_pattern.fullmatch(word):
        return "не существует"

    _error_dict = {
        200: "Успешно", 
        401: "Неправильный API", 
        402: "Текущий API ключ заблокирован",
        403: "Превышен лимит запросов", 
        413: "Превышен размер текста", 
        501: "Текущий язык не поддерживается",
        502: "Неверный параметр"
    }

    with open(srcFilePath, encoding="utf-8") as _get_word_file:
        words_dict = json.load(_get_word_file)

    if word in words_dict:
        return words_dict[word]

    with open(censorFilePath) as censor_file:
        worse_words = censor_file.read().split("\n")
    
    if any([re.fullmatch(worse_word, word) for worse_word in worse_words]):
        words_dict[word] = "мат"

        save_dict(words_dict)
        dictionary_search_logger.debug(f"its worse word")
        return "мат"

    url = (f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?"
        f"text={word}&flags=14&lang=ru-en&key={DICT_API}")

    req = await httpx_client.get(url)

    if req.status_code != 200:
        dictionary_search_logger.error(f"Doesn't loaded mean for word «{word}»! \n    Error: {_error_dict.get(req.status_code, req.status_code)}\n    Text: {req.text}")
        raise Exception(f"Doesn't loaded mean for word «{word}»")
    
    dictionary_search_logger.debug(f"Dumping mean")
    req_dict = json.loads(req.text)
    
    word_type = req_dict["def"][0]["pos"] if req_dict["def"] else "не существует"    
    words_dict[word] = word_type

    save_dict(words_dict)

    return word_type


def create_inline_button(text="", inline_query=None, switch=False, callback=None):
    """Create a button with switch inline query or with a callback."""
    if switch:
        return InlineKeyboardButton(text=text, switch_inline_query=inline_query, callback_data=callback)
    else:
        return InlineKeyboardButton(text=text, switch_inline_query_current_chat=inline_query, callback_data=callback)
