import dotenv
import json

def get_keys():
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
        DICT_API = input("Input your Yandex dictionary API (can be finded in https://yandex.ru/dev/dictionary/keys/get/?service=dict): ")
        BOT_API = input("Input your bot's token (can be finded in @botfather): ")

        dotenv.set_key(_dot_env_file, "DICT_API", DICT_API)
        dotenv.set_key(_dot_env_file, "BOT_API", BOT_API)

    else:
        DICT_API = dotenv.get_key(_dot_env_file, "DICT_API")
        BOT_API = dotenv.get_key(_dot_env_file, "BOT_API")
    
    return DICT_API, BOT_API


DICT_API, BOT_API = get_keys()