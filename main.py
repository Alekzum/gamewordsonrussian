from aiogram.filters import Command
from aiogram.types import Message, InlineQuery, CallbackQuery
from aiogram import Bot, Dispatcher, enums
from utils.my_filters import InlineLen, CallbackLen
from importlib import reload
import asyncio
import logging
import dotenv
import json

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


logging.basicConfig(level=logging.INFO)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)
aio_event_logger = logging.getLogger("aiogram.event")
aio_event_logger.setLevel(logging.WARNING)

bot = Bot(BOT_API, parse_mode=enums.ParseMode.HTML)
dp = Dispatcher()


@dp.message(Command("start"))
async def _cmd_start(message: Message):
    import scripts.cmd_start as cmd_start
    cmd_start = reload(cmd_start)
    await cmd_start.main(bot, message)


@dp.callback_query(CallbackLen(2))
async def _callback_continue(callback_query: CallbackQuery):
    import scripts.callback_continue as callback_continue
    callback_continue = reload(callback_continue)
    await callback_continue.main(bot, callback_query)


@dp.inline_query(InlineLen(2))
async def _inline_delete_game(inline_query: InlineQuery):
    import scripts.inline_game as inline_game
    inline_game = reload(inline_game)
    await inline_game.main(bot, inline_query)


@dp.inline_query(InlineLen(1))
async def _inline_start(inline_query: InlineQuery):
    import scripts.inline_start as inline_start
    inline_start = reload(inline_start)
    await inline_start.main(bot, inline_query)


@dp.inline_query(InlineLen(0))
async def _inline_info(inline_query: InlineQuery):
    import scripts.inline_start as inline_start
    inline_start = reload(inline_start)
    await inline_start.main(bot, inline_query)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
