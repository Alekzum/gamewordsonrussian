from aiogram.types import InlineQuery, CallbackQuery, InlineKeyboardButton
import utils.database as my_database
import logging
import dotenv
import httpx
import json
import re


# Подсказочки для любимого PyCharm
_config: dict[str: str]
_dot_env_file: str

# Создаём/извлекаем конфигурацию с .env файлом
try:
    with open("config.json", encoding="utf-8") as _file:
        _config = json.load(_file)
    _dot_env_file = _config["env_file"]
except FileNotFoundError:
    _dot_env_file = ".env" and input("Введите название файла с переменными (примеры: .env или env/.env):")
    _config = {"env_file": _dot_env_file}
    with open("config.json", "w", encoding="utf-8") as _file:
        json.dump(_config, _file, ensure_ascii=False)

# Пытаемся получить нужные АПИ
_env_in_dirs = dotenv.load_dotenv(_dot_env_file, verbose=True)
if not _env_in_dirs:
    DICT_API = input("Input your Yandex dictionary API "
                     "(can be finded in https://yandex.ru/dev/dictionary/keys/get/?service=dict): ")
    BOT_API = input("Input your bot's token (can be finded in @botfather): ")

    dotenv.set_key(_dot_env_file, "DICT_API", DICT_API)
    dotenv.set_key(_dot_env_file, "BOT_API", BOT_API)

else:
    DICT_API = dotenv.get_key(_dot_env_file, "DICT_API")
    BOT_API = dotenv.get_key(_dot_env_file, "BOT_API")


def inline_index(inline_query: InlineQuery, index: int):
    args = inline_query.query.split(" ") if inline_query.query != "" else []
    return len(args) >= (index+1) and args[index]


def callback_index(callback_query: CallbackQuery, index: int):
    args = callback_query.query.split(" ") if callback_query.query != "" else []
    return len(args) >= (index+1) and args[index]


httpx_client = httpx.AsyncClient()
rus_pattern = re.compile(r"([а-яА-Я]+)")
async def check_word(word: str) -> str | None:
    """Возвращает часть речи заданного слова или None, если возникла ошибка/такого нет."""
    global DICT_API, httpx_client
    word = word.lower()
    if not rus_pattern.fullmatch(word):
        return "не существует"
    _error_dict = {200: "Успешно", 401: "Неправильный API", 402: "Текущий API ключ заблокирован",
                   403: "Превышен лимит запросов", 413: "Превышен размер текста", 501: "Текущий язык не поддерживается",
                   502: "Неверный параметр"}

    with open("source/src_words.json", encoding="utf-8") as _get_word_file:
        words_dict = json.load(_get_word_file)

    if word in words_dict:
        return words_dict[word]

    else:
        url = (f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?"
               f"text={word}&flags=14&lang=ru-en&key={DICT_API}")
        logging.info(f"Trying to find {word}")
        req = await httpx_client.get(url)
        if req.status_code == 200:
            req_dict = json.loads(req.text)
            if len(req_dict["def"]) == 0:
                words_dict[word] = "не существует"
                with open("source/src_words.json", "w", encoding="utf-8") as _get_word_file:
                    json.dump(words_dict, _get_word_file, ensure_ascii=False, indent=4, sort_keys=True)
                return "не существует"
            else:
                word_type = req_dict["def"][0]["pos"]
                words_dict[word] = word_type
                with open("source/src_words.json", "w", encoding="utf-8") as _get_word_file:
                    json.dump(words_dict, _get_word_file, ensure_ascii=False, indent=4, sort_keys=True)

                return word_type

        else:
            logging.error(req.text)


def create_inline_button(text="", inline_query=None, switch=False, callback=None):
    """Create a button with switch inline query in current chat."""
    if switch:
        return InlineKeyboardButton(text=text, switch_inline_query=inline_query, callback_data=callback)
    else:
        return InlineKeyboardButton(text=text, switch_inline_query_current_chat=inline_query, callback_data=callback)


