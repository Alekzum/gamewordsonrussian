from aiogram.types import InlineQuery, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
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
        json.dump(_config, _file, ensure_ascii=False, indent=4, sort_keys=True)

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


httpx_client = httpx.AsyncClient()
rus_pattern = re.compile(r"([а-яА-Я]+)")
dictionary_search_logger = logging.getLogger("Yandex.Dict")


def inline_valid(inline_query: InlineQuery) -> bool:
    return (inline_query.query.count(".") == 1 and inline_query.query.count(" ") == 1 and
            re.fullmatch(rus_pattern, inline_query.query.split(" ")[1]))


async def check_word(word: str) -> str:
    """Возвращает часть речи заданного слова или "мат" | "не существует"."""
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
        with open("source/censor.txt") as censor_file:
            worse_words = censor_file.read().split("\n")
        for worse_word in worse_words:
            if re.fullmatch(worse_word, word):
                words_dict[word] = "мат"

                with open("source/src_words.json", "w", encoding="utf-8") as _get_word_file:
                    json.dump(words_dict, _get_word_file, ensure_ascii=False, indent=4, sort_keys=True)
                dictionary_search_logger.debug(f"its worse word")
                return "мат"

        url = (f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?"
               f"text={word}&flags=14&lang=ru-en&key={DICT_API}")

        req = await httpx_client.get(url)
        if req.status_code == 200:
            dictionary_search_logger.debug(f"Dumping mean")
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
            dictionary_search_logger.error(f"Doesn't loaded mean for word «{word}»! {req.text}")
            raise Exception(f"Doesn't loaded mean for word «{word}»")


def create_inline_button(text="", inline_query=None, switch=False, callback=None):
    """Create a button with switch inline query or with a callback."""
    if switch:
        return InlineKeyboardButton(text=text, switch_inline_query=inline_query, callback_data=callback)
    else:
        return InlineKeyboardButton(text=text, switch_inline_query_current_chat=inline_query, callback_data=callback)
